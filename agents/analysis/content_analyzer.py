#!/usr/bin/env python3
"""
This agent answers:
From the grounded content, what are the core concepts, facts, definitions,
equations, reactions, and relationships?
"""

# agents/analysis/content_analyzer.py

import logging
from typing import Dict, Any
from core.state import UserProfile, TutoringState, GroundedContext, PlannerOutput
from preprocessing.text_cleaner import clean_llm_string

logger = logging.getLogger(__name__)


def build_content_analyzer_prompt(
    task: Dict[str, Any],
    planning_context: Dict[str, str],
    grounded_context: GroundedContext,
) -> str:
    return f"""
You are a content analysis agent.

TASK PURPOSE:
{task["purpose"]}

EXPECTED OUTPUT:
{task["expected_output"]}

ACADEMIC CONTEXT:
Class: {planning_context.get("class", "")}
Board: {planning_context.get("board", "")}
Target Exam: {planning_context.get("target_exam", "")}
Subject: {planning_context.get("subject", "")}
Chapter: {planning_context.get("chapter", "")}
Sub-topic: {planning_context.get("sub_topic", "")}

SOURCE CONTENT (CLEANED IMAGE ANALYSIS):
{grounded_context.image_analysis}

RULES:
- Extract concepts, facts, definitions, equations, reactions, and relationships
- Organize information clearly using lists or sections
- Do NOT generate questions
- Do NOT include markdown
- Do NOT include commentary outside the content
"""


def content_analyzer_agent(
    llm,
    task: Dict[str, Any],
    state: TutoringState,
) -> Dict[str, Any]:
    """
    Extracts core academic content from the grounded context.
    """

    planning_context = state.plan.planning_context
    grounded_context = state.grounded_context

    logger.info("Running content analyzer")
    response = llm.invoke(
        build_content_analyzer_prompt(task, planning_context, grounded_context)
    )

    # Clean text output
    cleaned = clean_llm_string(response.content)

    return {
        "knowledge_base": {task["task_id"]: cleaned}
    }
