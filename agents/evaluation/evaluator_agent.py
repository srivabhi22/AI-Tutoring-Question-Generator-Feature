#!/usr/bin/env python3
"""
Are these answers correct, complete, well-structured, and aligned with the board/exam style?
"""

# agents/evaluation/evaluator_agent.py

from typing import Dict, Any
from core.state import TutoringState, UserProfile, PlannerOutput, GroundedContext
from preprocessing.text_cleaner import clean_llm_json


def build_evaluator_prompt(
    planning_context: Dict[str, str],
    question_bank: Dict[str, Any],
    solver_output: Dict[str, Any],
) -> str:
    return f"""
You are an expert examiner and teacher.

ACADEMIC CONTEXT:
Class: {planning_context["class"]}
Board: {planning_context["board"]}
Target Exam: {planning_context["target_exam"]}
Subject: {planning_context["subject"]}

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
{
  "overall_feedback": "",
  "mcq": [],
  "short_answer": [],
  "long_answer": []
}
"""


def evaluator_agent(
    llm,
    task: Dict[str, Any],
    state: TutoringState,
) -> Dict[str, Any]:
    """
    Evaluates solutions using exam-specific criteria.
    """

    planning_context = state["plan"]["planning_context"]
    question_bank = state["question_bank"]
    solver_output = state["solver_output"]

    response = llm.invoke(
        build_evaluator_prompt(
            planning_context,
            question_bank,
            solver_output,
        )
    )

    cleaned = clean_llm_json(response)

    return cleaned
