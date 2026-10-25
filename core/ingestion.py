"""
core/ingestion.py — CSV parsing, validation, deduplication, and record insertion.

Handles:
- Encoding detection and fallback (utf-8, utf-8-sig, latin-1, cp1252)
- Column mapping from arbitrary CSV headers to standard schema fields
- Validation (rejects empty/whitespace text, trims string fields)
- Exact deduplication via SHA-256 of normalized text
- Near-duplicate detection via SequenceMatcher (> 0.85 similarity ratio)
- Source register updates and comprehensive import summary
"""

import os
import hashlib
import io
from difflib import SequenceMatcher
from datetime import datetime, timezone
import pandas as pd

from core.database import get_connection, generate_id, now_iso


def normalize_text_for_hash(text: str) -> str:
    """Normalize text by lowercasing and collapsing whitespace."""
    if not text:
        return ""
    return " ".join(text.lower().split())


def compute_text_hash(text: str) -> str:
    """Compute SHA-256 hash of normalized text for exact deduplication."""
    norm = normalize_text_for_hash(text)
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


def read_csv_safe(file_or_path) -> pd.DataFrame:
    """
    Read CSV file or buffer with automatic encoding detection fallback.
    Tries utf-8, utf-8-sig, latin-1, cp1252.
    """
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    
    # If it's a Streamlit UploadedFile or BytesIO, read bytes once
    if hasattr(file_or_path, "read") and hasattr(file_or_path, "seek"):
        raw_bytes = file_or_path.read()
        file_or_path.seek(0)
        for enc in encodings:
            try:
                return pd.read_csv(io.BytesIO(raw_bytes), encoding=enc)
            except (UnicodeDecodeError, Exception):
                continue
        # Fallback to python engine with replace
        return pd.read_csv(io.BytesIO(raw_bytes), encoding="latin-1", on_bad_lines="skip")

    # If it's a file path string
    for enc in encodings:
        try:
            return pd.read_csv(file_or_path, encoding=enc)
        except (UnicodeDecodeError, Exception):
            continue
            
    return pd.read_csv(file_or_path, encoding="latin-1", on_bad_lines="skip")


def check_near_duplicate(text: str, existing_sample_texts: list[str], threshold: float = 0.85) -> tuple[bool, float, str]:
    """
    Check if text has a SequenceMatcher ratio > threshold against existing sample texts.
    Returns (is_near_dup, highest_ratio, matched_text).
    """
    norm_text = normalize_text_for_hash(text)
    if len(norm_text) < 15:
        # Too short for meaningful fuzzy matching
        return False, 0.0, ""

    best_ratio = 0.0
    best_match = ""
    for existing in existing_sample_texts:
        norm_existing = normalize_text_for_hash(existing)
        # Quick length filter before expensive SequenceMatcher
        len_diff = abs(len(norm_text) - len(norm_existing))
        max_len = max(len(norm_text), len(norm_existing))
        if max_len > 0 and (1.0 - (len_diff / max_len)) < threshold:
            continue
            
        ratio = SequenceMatcher(None, norm_text, norm_existing).quick_ratio()
        if ratio >= threshold:
            ratio = SequenceMatcher(None, norm_text, norm_existing).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = existing
                if ratio >= 0.98:
                    break

    return (best_ratio >= threshold), best_ratio, best_match


def import_csv(
    file_or_path,
    column_mapping: dict,
    source_name: str = "CSV Import",
    source_url: str = None,
    collection_method: str = "csv_import",
    record_type: str = "public_review",
    known_limitations: str = None,
    permission_notes: str = None,
    progress_callback = None
) -> dict:
    """
    Import records from a CSV file with validation and deduplication.

    Args:
        file_or_path: File path or file-like object (e.g. Streamlit UploadedFile)
        column_mapping: Dict mapping CSV column name -> Target schema column:
                        {'Review Text': 'text', 'Rating': 'rating', 'Date': 'publication_date', ...}
                        Target columns supported: 'text', 'source', 'source_url', 'rating', 'publication_date', 'respondent_id'
        source_name: Name of the data source
        source_url: Default URL if not in CSV
        collection_method: 'csv_import', 'google_forms_csv', etc.
        record_type: 'public_review', 'survey_response', etc.
        known_limitations: Source limitations for source_register
        permission_notes: Permissions notes for source_register
        progress_callback: Optional callable(current, total)

    Returns:
        Summary dict:
        {
            "total": int,
            "imported": int,
            "exact_duplicates": int,
            "near_duplicates": int,
            "rejected": int,
            "rejection_reasons": list of dicts,
            "source_id": str,
            "imported_ids": list of str
        }
    """
    df = read_csv_safe(file_or_path)
    total_rows = len(df)

    # Support both {target: csv_col} and {csv_col: target}
    target_to_csv = {}
    known_targets = {"text", "source", "source_url", "rating", "publication_date", "respondent_id"}
    for k, v in column_mapping.items():
        if not v or not k:
            continue
        if k in known_targets:
            target_to_csv[k] = v
        elif v in known_targets:
            target_to_csv[v] = k

    if "text" not in target_to_csv:
        raise ValueError("Column mapping must map at least one column to 'text'.")

    text_csv_col = target_to_csv["text"]
    if text_csv_col not in df.columns:
        raise ValueError(f"Mapped text column '{text_csv_col}' not found in CSV.")

    summary = {
        "total": total_rows,
        "imported": 0,
        "exact_duplicates": 0,
        "near_duplicates": 0,
        "rejected": 0,
        "rejection_reasons": [],
        "source_id": generate_id(),
        "imported_ids": []
    }

    with get_connection() as conn:
        # Load existing normalized text hashes from DB
        existing_rows = conn.execute("SELECT text FROM records").fetchall()
        existing_hashes = {compute_text_hash(row["text"]) for row in existing_rows}
        existing_sample_texts = [row["text"] for row in existing_rows if row["text"]]

        records_to_insert = []
        batch_hashes = set(existing_hashes)
        batch_sample_texts = list(existing_sample_texts)

        for idx, row in df.iterrows():
            row_num = idx + 1
            if progress_callback and total_rows > 0 and (idx % 10 == 0 or idx == total_rows - 1):
                progress_callback(idx + 1, total_rows)

            raw_text = row.get(text_csv_col)
            # 1. Validation: Reject null or empty/whitespace-only text
            if pd.isna(raw_text) or not str(raw_text).strip():
                summary["rejected"] += 1
                summary["rejection_reasons"].append({
                    "row": row_num,
                    "reason": "Empty or whitespace-only text field"
                })
                continue

            text_cleaned = str(raw_text).strip()

            # 2. Exact Deduplication
            text_hash = compute_text_hash(text_cleaned)
            if text_hash in batch_hashes:
                summary["exact_duplicates"] += 1
                continue

            # 3. Near Deduplication Check
            is_near, ratio, match_text = check_near_duplicate(text_cleaned, batch_sample_texts, threshold=0.85)
            duplicate_status = "unique"
            if is_near:
                summary["near_duplicates"] += 1
                duplicate_status = "near_duplicate_flagged"

            # Parse optional fields
            # Source
            source_val = source_name
            if "source" in target_to_csv and target_to_csv["source"] in df.columns:
                val = row.get(target_to_csv["source"])
                if pd.notna(val) and str(val).strip():
                    source_val = str(val).strip()

            # Source URL
            url_val = source_url
            if "source_url" in target_to_csv and target_to_csv["source_url"] in df.columns:
                val = row.get(target_to_csv["source_url"])
                if pd.notna(val) and str(val).strip():
                    url_val = str(val).strip()

            # Rating
            rating_val = None
            if "rating" in target_to_csv and target_to_csv["rating"] in df.columns:
                val = row.get(target_to_csv["rating"])
                if pd.notna(val):
                    try:
                        rating_val = float(str(val).strip())
                    except ValueError:
                        rating_val = None

            # Publication Date
            pub_date_val = None
            if "publication_date" in target_to_csv and target_to_csv["publication_date"] in df.columns:
                val = row.get(target_to_csv["publication_date"])
                if pd.notna(val) and str(val).strip():
                    pub_date_val = str(val).strip()

            # Respondent ID
            respondent_val = None
            if "respondent_id" in target_to_csv and target_to_csv["respondent_id"] in df.columns:
                val = row.get(target_to_csv["respondent_id"])
                if pd.notna(val) and str(val).strip():
                    respondent_val = str(val).strip()

            rec_id = generate_id()
            now_str = now_iso()

            record_dict = {
                "record_id": rec_id,
                "source": source_val,
                "record_type": record_type,
                "text": text_cleaned,
                "text_edited": None,
                "source_url": url_val,
                "publication_date": pub_date_val,
                "rating": rating_val,
                "collection_date": now_str,
                "collection_method": collection_method,
                "respondent_id": respondent_val,
                "duplicate_status": duplicate_status,
                "is_demo": 0,
                "created_at": now_str
            }

            records_to_insert.append(record_dict)
            batch_hashes.add(text_hash)
            # Add to sample texts for subsequent near-dedup check
            if len(batch_sample_texts) < 1000:
                batch_sample_texts.append(text_cleaned)

            summary["imported"] += 1
            summary["imported_ids"].append(rec_id)

        # Batch insert all accepted records
        if records_to_insert:
            columns = list(records_to_insert[0].keys())
            col_names = ", ".join(columns)
            placeholders = ", ".join(["?"] * len(columns))
            sql = f"INSERT INTO records ({col_names}) VALUES ({placeholders})"
            
            for rec in records_to_insert:
                conn.execute(sql, [rec[col] for col in columns])

        # Register source in source_register table
        if summary["imported"] > 0 or total_rows > 0:
            conn.execute(
                """
                INSERT INTO source_register 
                (source_id, source_name, collection_method, date_collected, record_count, known_limitations, permission_notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    summary["source_id"],
                    source_name,
                    collection_method,
                    now_iso(),
                    summary["imported"],
                    known_limitations or "Self-reported feedback; potential sampling and survivor bias.",
                    permission_notes or "Publicly accessible or user-provided survey data.",
                    now_iso()
                )
            )

    return summary
