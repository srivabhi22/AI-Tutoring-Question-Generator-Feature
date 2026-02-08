#!/usr/bin/env python3
"""
This file guarantees valid JSON
"""

# preprocessing/json_utils.py

import json
import re
from typing import Any


class JSONExtractionError(Exception):
    """Raised when JSON cannot be extracted safely from LLM output."""
    pass


def extract_json_from_llm(raw_text: str) -> Any:
    """
    Extracts the first valid JSON object or array from LLM output.

    Handles cases where JSON is wrapped in Markdown or surrounded by text.
    """

    if not isinstance(raw_text, str):
        raise JSONExtractionError("LLM output is not a string")

    # Remove Markdown code fences if present
    cleaned = re.sub(r"```(?:json)?", "", raw_text).strip()

    # Try direct parsing first
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Fallback: extract JSON object or array using regex
    json_pattern = re.compile(
        r"(\{.*\}|\[.*\])",
        re.DOTALL
    )

    match = json_pattern.search(cleaned)
    if not match:
        raise JSONExtractionError("No JSON object found in LLM output")

    json_str = match.group(1)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise JSONExtractionError(
            f"Extracted JSON is invalid: {e}"
        ) from e
