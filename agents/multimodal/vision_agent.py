#!/usr/bin/env python3
"""
This agent does exactly one thing:

Given an image + user profile,

It must:
1. Identify the subject, chapter, sub-topic
2. Explain what the image shows

This agent uses the Google Gemini multimodal API directly.
"""

# agents/multimodal/vision_agent.py

import logging
from typing import Dict, Any
from google import genai
from google.genai import types
import os
from core.state import UserProfile, GroundedContext
from preprocessing.json_utils import extract_json_from_llm, JSONExtractionError
from preprocessing.text_cleaner import clean_llm_json

logger = logging.getLogger(__name__)


def _get_env_value(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value


def build_multimodal_prompt(user_profile: UserProfile) -> str:
    return f"""
You are an expert curriculum analyst.

TASK:
1. Analyze the given educational image.
2. Identify the academic subject.
3. Identify the chapter and sub-topic most closely represented.
4. Describe clearly what the image shows.

RULES:
- Base your answer strictly on the image.
- Do NOT guess beyond what is visible.
- Output ONLY valid JSON.
- Do NOT include markdown.

OUTPUT FORMAT:
{{
  "metadata": {{
    "subject": "",
    "chapter": "",
    "sub_topic": ""
  }},
  "image_analysis": ""
}}

CONTEXT:
Student Class: {user_profile.class_level}
Board: {user_profile.board}
Target Exam: {user_profile.target_exam}
"""


def multimodal_vision_agent(
    image_base64: str,
    user_profile: UserProfile,
) -> GroundedContext:
    """
    Uses Gemini 3 Flash Preview to ground educational content from an image.
    """

    logger.info("Invoking multimodal model")
    prompt = build_multimodal_prompt(user_profile)
    client = genai.Client(api_key=_get_env_value("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model=_get_env_value("MULTIMODAL_MODEL_NAME"),
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_bytes(
                        data=bytes.fromhex(image_base64)
                        if image_base64.startswith("0x")
                        else __import__("base64").b64decode(image_base64),
                        mime_type="image/png",
                    ),
                    types.Part.from_text(text=prompt)
                ],
            )
        ],
    )

    # Gemini SDK returns plain text
    raw_text = response.text

    # Extract and clean JSON safely
    try:
        parsed = extract_json_from_llm(raw_text)
        cleaned = clean_llm_json(parsed)
        return GroundedContext(**cleaned)
    except JSONExtractionError as exc:
        logger.warning("Multimodal JSON parse failed, returning empty context: %s", exc)
        return GroundedContext(metadata={}, image_analysis=str(raw_text))
