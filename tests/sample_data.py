"""
tests/sample_data.py — Helper to load realistic initial demo dataset into the engine.
"""

import os
from core.ingestion import import_csv
from core.survey_ingestion import import_survey_csv

FIXTURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def load_sample_dataset() -> int:
    """
    Load both sample reviews CSV and survey responses CSV into the database.
    Returns total newly imported records.
    """
    total_imported = 0

    # 1. Load public reviews
    reviews_csv = os.path.join(FIXTURES_DIR, "sample_reviews.csv")
    if os.path.exists(reviews_csv):
        sum_rev = import_csv(
            file_or_path=reviews_csv,
            column_mapping={
                "text": "Review_Text",
                "rating": "Rating",
                "publication_date": "Review_Date",
                "source_url": "URL"
            },
            source_name="Google Play Store",
            source_url="https://play.google.com/store/apps/details?id=com.nextbillion.groww",
            record_type="public_review",
            known_limitations="Public app store reviews skew towards vocal dissatisfaction and operational friction."
        )
        total_imported += sum_rev["imported"]

    # 2. Load Google Forms survey responses
    survey_csv = os.path.join(FIXTURES_DIR, "sample_survey.csv")
    if os.path.exists(survey_csv):
        sum_surv = import_survey_csv(
            file_or_path=survey_csv,
            open_text_col="Detailed_Experience_Feedback",
            respondent_id_col="Respondent_Email",
            context_cols=[
                ("SIP_Continuation_Status", "SIP Status"),
                ("Investor_Experience", "Experience"),
                ("Primary_Dropoff_Reasons", "Dropoff Triggers")
            ],
            source_name="SIP Investor Drop-off Survey Wave 1",
            known_limitations="Self-selected survey cohort; responses may over-represent proactive or highly frustrated users."
        )
        total_imported += sum_surv["imported"]

    return total_imported
