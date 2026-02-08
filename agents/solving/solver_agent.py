#!/usr/bin/env python3
"""
Given the generated questions, what are the correct, well-explained solutions?
"""


from typing import Dict, Any, cast
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from core.state import TutoringState, UserProfile, PlannerOutput, GroundedContext
from tools.math_solver import python_math
from preprocessing.json_utils import extract_json_from_llm
from preprocessing.text_cleaner import clean_llm_json


def build_solver_instruction(
    planning_context: Dict[str, str],
    question_bank: Dict[str, Any],
) -> str:
    return f"""
You are a solution-writing agent.

ACADEMIC CONTEXT:
Class: {planning_context["class"]}
Board: {planning_context["board"]}
Target Exam: {planning_context["target_exam"]}
Subject: {planning_context["subject"]}

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

    planning_context = state["plan"]["planning_context"]
    question_bank = state["question_bank"]

    solver_prompt = build_solver_instruction(
        planning_context,
        question_bank
    )

    # Create ReAct agent (modern API)
    react_solver = create_agent(
        model=llm,
        tools=[python_math]
    )

    # Invoke solver (ReAct agents expect 'input')
    result = react_solver.invoke(
        cast(Any, solver_prompt)
    )
    # Extract final message
    final_output = result["messages"][-1].content

    parsed = extract_json_from_llm(final_output)
    cleaned = clean_llm_json(parsed)

    return cleaned
