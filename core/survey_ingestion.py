"""
core/survey_ingestion.py — Google Forms Survey CSV specialization.

Handles:
- Preserving comma-separated checkbox responses
- Respondent ID tracking (from mapped column or auto-generated sequential ID)
- Multi-question contextual formatting (SIP status, experience level, open feedback)
- Setting record_type='survey_response' and collection_method='google_forms_csv'
- Distinct source registration
"""

import pandas as pd
from core.database import get_connection, generate_id, now_iso
from core.ingestion import (
    read_csv_safe,
    compute_text_hash,
    check_near_duplicate,
    normalize_text_for_hash
)


def import_survey_csv(
    file_or_path,
    open_text_col: str,
    respondent_id_col: str = None,
    context_cols: list[tuple[str, str]] = None,
    source_name: str = "Google Forms Survey",
    known_limitations: str = None,
    permission_notes: str = None,
    progress_callback = None
) -> dict:
    """
    Import survey responses from a Google Forms CSV export.

    Args:
        file_or_path: File path or file-like object
        open_text_col: Primary open-text response column name
        respondent_id_col: Column for respondent identifier (e.g. Timestamp, email, or custom ID).
                           If None, auto-generated sequential IDs (RESP-0001, etc.) are used.
        context_cols: List of (column_name, label) tuples for context questions,
                      e.g. [('SIP Experience', 'Experience'), ('Current Status', 'Continuation Status')]
        source_name: Survey dataset name
        known_limitations: Known methodological limitations
        permission_notes: Consent or permission notes
        progress_callback: Optional progress callable(current, total)

    Returns:
        Summary dict
    """
    df = read_csv_safe(file_or_path)
    total_rows = len(df)

    if open_text_col not in df.columns:
        raise ValueError(f"Open-text column '{open_text_col}' not found in CSV.")

    context_cols = context_cols or []

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

            raw_open_text = row.get(open_text_col)
            # Validation: reject if open-text is blank
            if pd.isna(raw_open_text) or not str(raw_open_text).strip():
                summary["rejected"] += 1
                summary["rejection_reasons"].append({
                    "row": row_num,
                    "reason": "Missing or blank response in primary open-text column"
                })
                continue

            cleaned_open_text = str(raw_open_text).strip()

            # Compose context header if additional questions were mapped
            # Checkbox values with commas are preserved as-is
            context_parts = []
            for col_name, label in context_cols:
                if col_name in df.columns:
                    val = row.get(col_name)
                    if pd.notna(val) and str(val).strip():
                        # Preserve comma-separated checkbox selections cleanly
                        context_parts.append(f"[{label}: {str(val).strip()}]")

            if context_parts:
                composed_text = f"{' '.join(context_parts)}\n{cleaned_open_text}"
            else:
                composed_text = cleaned_open_text

            # Deduplication
            text_hash = compute_text_hash(composed_text)
            if text_hash in batch_hashes:
                summary["exact_duplicates"] += 1
                continue

            is_near, ratio, match_text = check_near_duplicate(composed_text, batch_sample_texts, threshold=0.85)
            duplicate_status = "unique"
            if is_near:
                summary["near_duplicates"] += 1
                duplicate_status = "near_duplicate_flagged"

            # Respondent ID
            if respondent_id_col and respondent_id_col in df.columns:
                resp_val = row.get(respondent_id_col)
                resp_id = str(resp_val).strip() if pd.notna(resp_val) else f"RESP-{idx+1:04d}"
            else:
                resp_id = f"RESP-{idx+1:04d}"

            rec_id = generate_id()
            now_str = now_iso()

            record_dict = {
                "record_id": rec_id,
                "source": source_name,
                "record_type": "survey_response",
                "text": composed_text,
                "text_edited": None,
                "source_url": None,
                "publication_date": None,
                "rating": None,
                "collection_date": now_str,
                "collection_method": "google_forms_csv",
                "respondent_id": resp_id,
                "duplicate_status": duplicate_status,
                "is_demo": 0,
                "created_at": now_str
            }

            records_to_insert.append(record_dict)
            batch_hashes.add(text_hash)
            if len(batch_sample_texts) < 1000:
                batch_sample_texts.append(composed_text)

            summary["imported"] += 1
            summary["imported_ids"].append(rec_id)

        if records_to_insert:
            columns = list(records_to_insert[0].keys())
            col_names = ", ".join(columns)
            placeholders = ", ".join(["?"] * len(columns))
            sql = f"INSERT INTO records ({col_names}) VALUES ({placeholders})"
            for rec in records_to_insert:
                conn.execute(sql, [rec[col] for col in columns])

        # Source register entry
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
                    "google_forms_csv",
                    now_iso(),
                    summary["imported"],
                    known_limitations or "Self-selected survey cohort; responses may over-represent proactive respondents.",
                    permission_notes or "Informed consent obtained via survey preamble; anonymized respondent IDs.",
                    now_iso()
                )
            )

    return summary
