"""
migrate_records_schema.py
Safely adds source_category, title, and processing_status to records table if they don't exist.
Categorizes existing records into 'primary' and 'secondary'.
Preserves all existing data.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "sip_discovery.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Inspect existing columns
    existing_cols = [c[1] for c in cursor.execute("PRAGMA table_info(records)").fetchall()]
    print(f"Existing columns in records: {existing_cols}")

    # 2. Add columns if missing
    if "source_category" not in existing_cols:
        cursor.execute("ALTER TABLE records ADD COLUMN source_category TEXT DEFAULT 'secondary'")
        print("Added column: source_category")

    if "title" not in existing_cols:
        cursor.execute("ALTER TABLE records ADD COLUMN title TEXT")
        print("Added column: title")

    if "processing_status" not in existing_cols:
        cursor.execute("ALTER TABLE records ADD COLUMN processing_status TEXT DEFAULT 'processed'")
        print("Added column: processing_status")

    # 3. Categorize existing records:
    # Primary: Google Forms survey, Primary Survey, interview_note, survey_response
    cursor.execute("""
        UPDATE records 
        SET source_category = 'primary'
        WHERE source LIKE '%Primary%' 
           OR record_type IN ('survey_response', 'interview_note')
           OR collection_method = 'google_forms_csv'
    """)

    # Secondary: public_review, browser_collected, secondary_article, Play Store, Trustpilot
    cursor.execute("""
        UPDATE records 
        SET source_category = 'secondary'
        WHERE record_type IN ('public_review', 'browser_collected', 'secondary_article')
           OR source IN ('Play Store', 'Trustpilot', 'Google Play Store')
           OR collection_method IN ('chrome_extension', 'url_fetch', 'csv_import')
    """)

    # Update titles for existing records if null
    cursor.execute("""
        UPDATE records 
        SET title = CASE 
            WHEN source_category = 'primary' THEN 'Primary Survey Feedback [' || coalesce(respondent_id, record_id) || ']'
            WHEN source = 'Play Store' THEN 'Play Store Review'
            WHEN source = 'Trustpilot' THEN 'Trustpilot Public Review'
            WHEN source = 'Google Play Store' THEN 'Play Store Extension Capture'
            ELSE source || ' Feedback'
        END
        WHERE title IS NULL
    """)

    conn.commit()

    # 4. Report counts
    primary_count = cursor.execute("SELECT count(*) FROM records WHERE source_category = 'primary'").fetchone()[0]
    secondary_count = cursor.execute("SELECT count(*) FROM records WHERE source_category = 'secondary'").fetchone()[0]
    total_count = cursor.execute("SELECT count(*) FROM records").fetchone()[0]

    print("\n--- Migration Complete ---")
    print(f"Primary records: {primary_count}")
    print(f"Secondary records: {secondary_count}")
    print(f"Total records in DB: {total_count}")

    conn.close()

if __name__ == "__main__":
    migrate()
