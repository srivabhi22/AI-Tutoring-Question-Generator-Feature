#!/usr/bin/env python3
"""
This agent does exactly one thing:

Given a user profile + grounded context (from image)

It must:
1. Break the goal into subtasks
2. Assign each subtask to valid agent IDs only
3. Output a strict JSON plan
"""

import logging
from typing import Dict, Any

from core.state import UserProfile, GroundedContext, PlannerOutput
from config.planner_constraints import PLANNER_SYSTEM_PROMPT
from preprocessing.json_utils import extract_json_from_llm, JSONExtractionError
from preprocessing.text_cleaner import clean_llm_json

logger = logging.getLogger(__name__)

def build_planner_input(
    user_profile: UserProfile,
    grounded_context: GroundedContext,
) -> str:
    """
    Builds the user message for the planner LLM.
    """

    return f"""
USER PROFILE:
Class: {user_profile.class_level}
Board: {user_profile.board}
Target Exam: {user_profile.target_exam}

GROUNDED CONTEXT:
Subject: {grounded_context.metadata.get("subject", "")}
Chapter: {grounded_context.metadata.get("chapter", "")}
Sub-topic: {grounded_context.metadata.get("sub_topic", "")}

Image Analysis:
{grounded_context.image_analysis}
"""


def planner_agent(
    llm,
    user_profile: UserProfile,
    grounded_context: GroundedContext,
) -> PlannerOutput:
    """
    Calls the planner LLM to produce a task execution plan.
    """

    logger.info("Invoking planner LLM")
    response = llm.invoke(
        [
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": build_planner_input(user_profile, grounded_context)},
        ]
    )

    # Extract and clean JSON
    try:
        parsed = extract_json_from_llm(response.content)
        cleaned = clean_llm_json(parsed)
        logger.info("Planner LLM response parsed")
        return PlannerOutput(**cleaned)
    except JSONExtractionError as exc:
        logger.warning("Planner JSON parse failed: %s", exc)
        raise
