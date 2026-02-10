#!/usr/bin/env python3
"""
This agent answers:
Given the content and exam pattern,
what types of questions should be created,
at what difficulty, and with what distractor logic?
"""


import logging
from typing import Dict, Any

from core.state import TutoringState
from preprocessing.text_cleaner import clean_llm_string

logger = logging.getLogger(__name__)


def build_question_design_prompt(
    task: Dict[str, Any],
    planning_context: Dict[str, str],
    extracted_content: str,
    exam_analysis: str,
) -> str:
    return f"""
You are a question design agent.

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

EXAM PATTERN ANALYSIS:
{exam_analysis}

RULES:
- Decide appropriate question types (MCQ, short answer, numerical, etc.)
- Decide difficulty distribution (easy / medium / hard)
- Specify conceptual focus and skills tested
- Design common distractor ideas or misconceptions
- Do NOT generate actual questions
- Do NOT include markdown
- Do NOT include commentary outside design
"""


def question_designer_agent(
    llm,
    task: Dict[str, Any],
    state: TutoringState,
) -> Dict[str, Any]:
    """
    Designs question intent, difficulty, and distractors.
    """

    planning_context = state.plan.planning_context

    extracted_content = state.knowledge_base.get("content_analyzer", "")
    exam_analysis = state.knowledge_base.get("exam_pattern_analyst", "")

    logger.info("Running question designer")
    response = llm.invoke(
        build_question_design_prompt(
            task,
            planning_context,
            extracted_content,
            exam_analysis,
        )
    )

    cleaned = clean_llm_string(response.content)

    return {
        "knowledge_base": {task["task_id"]: cleaned}
    }
