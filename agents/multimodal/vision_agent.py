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

from typing import Dict, Any
from google import genai
import os
from core.state import UserProfile, GroundedContext
from preprocessing.json_utils import extract_json_from_llm
from preprocessing.text_cleaner import clean_llm_json


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
Student Class: {user_profile["class_level"]}
Board: {user_profile["board"]}
Target Exam: {user_profile["target_exam"]}
"""


def multimodal_vision_agent(
    image_base64: str,
    user_profile: UserProfile,
) -> GroundedContext:
    """
    Uses Gemini 3 Flash Preview to ground educational content from an image.
    """

    prompt = build_multimodal_prompt(user_profile)
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model=os.getenv("MULTIMODAL_MODEL_NAME"),
        contents=[
            {
                "role": "user",
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": image_base64,
                        }
                    },
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    )

    # Gemini SDK returns plain text
    raw_text = response.text

    # Extract and clean JSON safely
    parsed = extract_json_from_llm(raw_text)
    cleaned = clean_llm_json(parsed)

    return cleaned
