#!/usr/bin/env python3
"""
Are these answers correct, complete, well-structured, and aligned with the board/exam style?
"""

# agents/evaluation/evaluator_agent.py

import logging
from typing import Dict, Any
from core.state import TutoringState, UserProfile, PlannerOutput, GroundedContext
from preprocessing.json_utils import extract_json_from_llm, JSONExtractionError
from preprocessing.text_cleaner import clean_llm_json

logger = logging.getLogger(__name__)


def build_evaluator_prompt(
    planning_context: Dict[str, str],
    question_bank: Dict[str, Any],
    solver_output: Dict[str, Any],
) -> str:
    return f"""
You are an expert examiner and teacher.

ACADEMIC CONTEXT:
Class: {planning_context.get("class", "")}
Board: {planning_context.get("board", "")}
Target Exam: {planning_context.get("target_exam", "")}
Subject: {planning_context.get("subject", "")}

QUESTIONS:
{question_bank}

STUDENT ANSWERS (SOLVER OUTPUT):
{solver_output}

RULES:
- Evaluate correctness and completeness
- Check conceptual coverage
- Judge answer quality as per board/exam standards
- Suggest concrete improvements
- Do NOT rewrite answers
- Do NOT include markdown
- Do NOT include commentary outside evaluation

OUTPUT FORMAT:
{{
  "overall_feedback": "",
  "mcq": [],
  "short_answer": [],
  "long_answer": []
}}
"""


def evaluator_agent(
    llm,
    task: Dict[str, Any],
    state: TutoringState,
) -> Dict[str, Any]:
    """
    Evaluates solutions using exam-specific criteria.
    """

    planning_context = state.plan.planning_context
    question_bank = state.question_bank
    solver_output = state.solver_output

    logger.info("Running evaluator")
    response = llm.invoke(
        build_evaluator_prompt(
            planning_context,
            question_bank,
            solver_output,
        )
    )

    try:
        parsed = extract_json_from_llm(response.content)
        cleaned = clean_llm_json(parsed)
    except JSONExtractionError as exc:
        logger.warning("Evaluator JSON parse failed: %s", exc)
        cleaned = {
            "overall_feedback": "Evaluator output could not be parsed.",
            "mcq": [],
            "short_answer": [],
            "long_answer": [],
        }

    if isinstance(cleaned, list):
        cleaned = {
            "overall_feedback": "Evaluator returned a list; wrapped for safety.",
            "mcq": cleaned,
            "short_answer": [],
            "long_answer": [],
        }
    elif not isinstance(cleaned, dict):
        cleaned = {
            "overall_feedback": "Evaluator output was not a dict; coerced.",
            "mcq": [],
            "short_answer": [],
            "long_answer": [],
        }

    return {
        "evaluation": cleaned,
        "knowledge_base": {task["task_id"]: cleaned},
    }
