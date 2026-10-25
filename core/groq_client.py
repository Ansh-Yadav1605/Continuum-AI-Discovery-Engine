"""
core/groq_client.py — Groq API wrapper with connection diagnostic, error handling, and batch analysis.

Features:
- 5-step connection diagnostic per architecture.md specification
- Safe JSON mode completions with schema extraction
- Rate limit, network error, and auth exception handling
- Batch analysis with progress callback
- Never triggers API calls automatically on import or app start
"""

import os
import json
import re
import time
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

from core.prompts import SYSTEM_PROMPT, build_user_prompt, TAXONOMY_THEMES

# Ensure .env is loaded
load_dotenv()

DEFAULT_MODEL = "llama-3.3-70b-versatile"


def get_api_key() -> Optional[str]:
    """Retrieve Groq API key from environment, checking aliases."""
    return os.getenv("GROQ_API_KEY") or os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY")


def get_model_name() -> str:
    """Retrieve configured Groq model name from environment."""
    return os.getenv("GROQ_MODEL") or DEFAULT_MODEL


def get_client():
    """
    Instantiate and return the Groq SDK client.
    Raises ValueError if API key is not configured.
    """
    key = get_api_key()
    if not key or key == "your_key_here":
        raise ValueError("GROQ_API_KEY is not configured in .env")
    
    from groq import Groq
    return Groq(api_key=key)


def test_connection() -> Dict[str, Any]:
    """
    Run 5-step diagnostic check on the Groq API connection:
      1. Check if GROQ_API_KEY is configured
      2. Call client.models.list() to verify reachability
      3. Confirm authentication succeeds
      4. Check if GROQ_MODEL appears in model list
      5. Send a tiny test prompt ("Reply with OK") and verify response

    Returns dict with summary:
      {
        "all_passed": bool,
        "steps": [
          {"step": int, "name": str, "success": bool, "message": str}
        ]
      }
    """
    steps = []
    
    # Step 1: Key Check
    key = get_api_key()
    if not key or key == "your_key_here" or not key.strip():
        steps.append({
            "step": 1,
            "name": "API Key Check",
            "success": False,
            "message": "GROQ_API_KEY is not configured. Create a .env file from .env.example and set your key."
        })
        return {"all_passed": False, "steps": steps}
    
    masked_key = key[:6] + "..." + key[-4:] if len(key) > 10 else "***"
    steps.append({
        "step": 1,
        "name": "API Key Check",
        "success": True,
        "message": f"API key configured ({masked_key})"
    })

    # Steps 2 & 3: Reachability and Auth
    try:
        from groq import Groq, AuthenticationError, APIConnectionError, APIError
        client = Groq(api_key=key)
        models_resp = client.models.list()
        available_models = [m.id for m in models_resp.data]
        
        steps.append({
            "step": 2,
            "name": "API Reachability",
            "success": True,
            "message": "Successfully contacted api.groq.com"
        })
        steps.append({
            "step": 3,
            "name": "Authentication",
            "success": True,
            "message": "Authentication successful"
        })
    except AuthenticationError as e:
        steps.append({
            "step": 2,
            "name": "API Reachability",
            "success": True,
            "message": "Successfully reached api.groq.com"
        })
        steps.append({
            "step": 3,
            "name": "Authentication",
            "success": False,
            "message": f"Authentication failed: {str(e)}. Please check your key at console.groq.com."
        })
        return {"all_passed": False, "steps": steps}
    except APIConnectionError as e:
        steps.append({
            "step": 2,
            "name": "API Reachability",
            "success": False,
            "message": f"Cannot reach api.groq.com: {str(e)}. Check internet connection or network firewall."
        })
        return {"all_passed": False, "steps": steps}
    except Exception as e:
        steps.append({
            "step": 2,
            "name": "API Reachability",
            "success": False,
            "message": f"Connection check failed: {str(e)}"
        })
        return {"all_passed": False, "steps": steps}

    # Step 4: Model check
    target_model = get_model_name()
    if target_model in available_models:
        steps.append({
            "step": 4,
            "name": "Model Availability",
            "success": True,
            "message": f"Model '{target_model}' is available on Groq."
        })
    else:
        # Check if any fallback model exists
        steps.append({
            "step": 4,
            "name": "Model Availability",
            "success": False,
            "message": f"Model '{target_model}' not found. Available models include: {', '.join(available_models[:5])}"
        })
        return {"all_passed": False, "steps": steps}

    # Step 5: Test Prompt
    try:
        completion = client.chat.completions.create(
            model=target_model,
            messages=[{"role": "user", "content": "Reply with 'OK'."}],
            max_tokens=10,
            temperature=0.0
        )
        content = completion.choices[0].message.content.strip()
        steps.append({
            "step": 5,
            "name": "Test Completion",
            "success": True,
            "message": f"Completion test succeeded. Model replied: '{content}'"
        })
    except Exception as e:
        steps.append({
            "step": 5,
            "name": "Test Completion",
            "success": False,
            "message": f"Test completion request failed: {str(e)}"
        })
        return {"all_passed": False, "steps": steps}

    return {"all_passed": True, "steps": steps}


def clean_json_text(text: str) -> str:
    """Strip markdown code fence blocks if returned by the LLM."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def validate_schema(data: dict) -> tuple[bool, list[str]]:
    """Validate parsed JSON against expected Phase 1 analysis schema."""
    errors = []
    
    valid_relevance = {"directly_relevant", "indirectly_relevant", "not_relevant", "ambiguous"}
    rel = data.get("relevance")
    if rel not in valid_relevance:
        errors.append(f"Invalid relevance '{rel}'. Must be one of {valid_relevance}")

    themes = data.get("themes")
    if not isinstance(themes, list):
        errors.append("Field 'themes' must be a list")

    required_keys = [
        "relevance", "relevance_explanation", "evidence_excerpt", "themes",
        "behaviour", "user_need", "workaround", "journey_stage",
        "continuation_mention", "missing_context", "explanation"
    ]
    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required field: '{key}'")

    return (len(errors) == 0, errors)


def analyse_record(record: dict, model: Optional[str] = None) -> Dict[str, Any]:
    """
    Send a single record to Groq for classification and evidence extraction.
    Returns parsed and validated response dict.
    """
    client = get_client()
    target_model = model or get_model_name()
    prompt = build_user_prompt(record)

    from groq import RateLimitError, APIError, APIConnectionError

    try:
        response = client.chat.completions.create(
            model=target_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=1000
        )
    except RateLimitError as e:
        raise RuntimeError(f"Groq Rate Limit exceeded: {str(e)}. Please wait before retrying.") from e
    except APIConnectionError as e:
        raise ConnectionError(f"Cannot reach api.groq.com: {str(e)}") from e
    except APIError as e:
        raise RuntimeError(f"Groq API Error: {str(e)}") from e

    raw_content = response.choices[0].message.content
    cleaned_content = clean_json_text(raw_content)

    try:
        parsed = json.loads(cleaned_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model failed to return valid JSON: {str(e)}\nRaw output: {raw_content[:200]}") from e

    is_valid, validation_errors = validate_schema(parsed)
    if not is_valid:
        # If minor schema mismatch, populate missing keys with defaults
        for k in ["relevance", "relevance_explanation", "evidence_excerpt", "themes", "behaviour", "user_need", "workaround", "journey_stage", "continuation_mention", "missing_context", "explanation"]:
            if k not in parsed:
                parsed[k] = [] if k == "themes" else None
        if parsed.get("relevance") not in {"directly_relevant", "indirectly_relevant", "not_relevant", "ambiguous"}:
            parsed["relevance"] = "ambiguous"

    parsed["model_used"] = target_model
    return parsed


def analyse_batch(
    records: List[dict],
    batch_size: int = 5,
    progress_callback = None,
    delay_between_records: float = 0.2
) -> Dict[str, Any]:
    """
    Analyse a batch of records sequentially with rate-limit respect and progress reporting.

    Returns summary:
    {
      "total": int,
      "analysed": int,
      "errors": int,
      "results": list of (record_id, parsed_result_or_none, error_message_or_none)
    }
    """
    total = len(records)
    summary = {
        "total": total,
        "analysed": 0,
        "errors": 0,
        "results": []
    }

    for idx, rec in enumerate(records):
        rec_id = rec.get("record_id")
        if progress_callback:
            progress_callback(idx + 1, total, rec_id)

        try:
            result = analyse_record(rec)
            summary["analysed"] += 1
            summary["results"].append({
                "record_id": rec_id,
                "success": True,
                "data": result,
                "error": None
            })
        except Exception as e:
            summary["errors"] += 1
            summary["results"].append({
                "record_id": rec_id,
                "success": False,
                "data": None,
                "error": str(e)
            })

        if delay_between_records > 0 and idx < total - 1:
            time.sleep(delay_between_records)

    return summary
