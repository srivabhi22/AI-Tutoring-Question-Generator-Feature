#!/usr/bin/env python3
"""
This agent answers:
Given the extracted content, how is this usually tested in the target exam?
"""



import logging
from typing import Dict, Any

from core.state import TutoringState
from preprocessing.text_cleaner import clean_llm_string

logger = logging.getLogger(__name__)


def build_exam_pattern_prompt(
    task: Dict[str, Any],
    planning_context: Dict[str, str],
    extracted_content: str,
) -> str:
    return f"""
You are an exam pattern analysis agent.

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

EXTRACTED CONTENT:
{extracted_content}

RULES:
- Analyze how this content is commonly tested in the given exam
- Identify typical question formats (conceptual, numerical, MCQ, short answer, etc.)
- Highlight common mistakes and traps
- Indicate expected depth (definition-level, derivation-level, application-level)
- Do NOT generate questions
- Do NOT include markdown
- Do NOT include commentary outside analysis
"""


def exam_pattern_analyst_agent(
    llm,
    task: Dict[str, Any],
    state: TutoringState,
) -> Dict[str, Any]:
    """
    Analyzes exam relevance and testing patterns for extracted content.
    """

    planning_context = state.plan.planning_context

    # Get output from content analyzer
    extracted_content = ""
    for key, value in state.knowledge_base.items():
        if "extract" in key or "content" in key:
            extracted_content = value
            break

    logger.info("Running exam pattern analyst")
    response = llm.invoke(
        build_exam_pattern_prompt(task, planning_context, extracted_content)
    )

    cleaned = clean_llm_string(response.content)

    return {
        "knowledge_base": {task["task_id"]: cleaned}
    }
