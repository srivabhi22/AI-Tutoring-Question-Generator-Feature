#!/usr/bin/env python3
"""
Given the generated questions, what are the correct, well-explained solutions?
"""


import logging
from typing import Dict, Any
from core.state import TutoringState, UserProfile, PlannerOutput, GroundedContext
from preprocessing.json_utils import extract_json_from_llm, JSONExtractionError
from preprocessing.text_cleaner import clean_llm_json

logger = logging.getLogger(__name__)

def build_solver_instruction(
    planning_context: Dict[str, str],
    question_bank: Dict[str, Any],
) -> str:
    return f"""
You are a solution-writing agent.

ACADEMIC CONTEXT:
Class: {planning_context.get("class", "")}
Board: {planning_context.get("board", "")}
Target Exam: {planning_context.get("target_exam", "")}
Subject: {planning_context.get("subject", "")}

QUESTIONS:
{question_bank}

RULES:
- Solve questions step-by-step
- Use tools ONLY if calculation is required
- Ensure final answers are correct
- Output ONLY valid JSON
- Do NOT include markdown
- Do NOT explain your reasoning outside the solution field

OUTPUT FORMAT:
{{
  "mcq": [],
  "short_answer": [],
  "long_answer": []
}}
"""


def solver_agent(
    llm,
    task: Dict[str, Any],
    state: TutoringState,
) -> Dict[str, Any]:
    """
    ReAct-based solver agent with math tool support.
    """

    planning_context = state.plan.planning_context
    question_bank = state.question_bank

    solver_prompt = build_solver_instruction(
        planning_context,
        question_bank
    )

    logger.info("Running solver")
    if llm is None or not hasattr(llm, "invoke"):
        raise RuntimeError("LLM is not configured for solver agent")

    response = llm.invoke(solver_prompt)
    content = response.content if hasattr(response, "content") else response

    try:
        parsed = extract_json_from_llm(content)
        cleaned = clean_llm_json(parsed)
    except JSONExtractionError as exc:
        logger.warning("Solver JSON parse failed: %s", exc)
        cleaned = {"mcq": [], "short_answer": [], "long_answer": []}

    if isinstance(cleaned, list):
        cleaned = {
            "mcq": cleaned,
            "short_answer": [],
            "long_answer": [],
        }
    elif not isinstance(cleaned, dict):
        cleaned = {"mcq": [], "short_answer": [], "long_answer": []}

    return {
        "solver_output": cleaned,
        "knowledge_base": {task["task_id"]: cleaned},
    }
