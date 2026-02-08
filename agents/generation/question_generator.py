#!/usr/bin/env python3
"""
Based on everything decided so far, generate the actual questions and answers.
"""

# agents/generation/question_generator.py

from typing import Dict, Any
from core.state import TutoringState, UserProfile, PlannerOutput, GroundedContext
from preprocessing.json_utils import extract_json_from_llm
from preprocessing.text_cleaner import clean_llm_json


def build_question_generator_prompt(
    task: Dict[str, Any],
    planning_context: Dict[str, str],
    knowledge_base: Dict[str, Any],
) -> str:
    return f"""
You are a question generation agent.

TASK PURPOSE:
{task["purpose"]}

EXPECTED OUTPUT:
{task["expected_output"]}

ACADEMIC CONTEXT:
Class: {planning_context["class"]}
Board: {planning_context["board"]}
Target Exam: {planning_context["target_exam"]}
Subject: {planning_context["subject"]}
Chapter: {planning_context["chapter"]}
Sub-topic: {planning_context["sub_topic"]}

KNOWLEDGE BASE:
{knowledge_base}

RULES:
- Generate questions strictly based on the knowledge base
- Follow the question design guidance
- Output ONLY valid JSON
- Do NOT include markdown
- Do NOT include commentary
- Do NOT invent topics

OUTPUT FORMAT:
{
  "mcq": [],
  "short_answer": [],
  "long_answer": []
}
"""


def question_generator_agent(
    llm,
    task: Dict[str, Any],
    state: TutoringState,
) -> Dict[str, Any]:
    """
    Generates final exam-aligned questions.
    """

    planning_context = state["plan"]["planning_context"]
    knowledge_base = state["knowledge_base"]

    response = llm.invoke(
        build_question_generator_prompt(
            task,
            planning_context,
            knowledge_base,
        )
    )

    parsed = extract_json_from_llm(response)
    cleaned = clean_llm_json(parsed)

    return cleaned
