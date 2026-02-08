#!/usr/bin/env python3
"""
This agent answers:
Given the content and exam pattern,
what types of questions should be created,
at what difficulty, and with what distractor logic?
"""


from typing import Dict, Any

from preprocessing.text_cleaner import clean_llm_string


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
Class: {planning_context["class"]}
Board: {planning_context["board"]}
Target Exam: {planning_context["target_exam"]}
Subject: {planning_context["subject"]}
Chapter: {planning_context["chapter"]}
Sub-topic: {planning_context["sub_topic"]}

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
    state: Dict[str, Any],
) -> str:
    """
    Designs question intent, difficulty, and distractors.
    """

    planning_context = state["plan"]["planning_context"]

    extracted_content = ""
    exam_analysis = ""

    for key, value in state["knowledge_base"].items():
        if "extract" in key or "content" in key:
            extracted_content = value
        if "exam" in key:
            exam_analysis = value

    response = llm.invoke(
        build_question_design_prompt(
            task,
            planning_context,
            extracted_content,
            exam_analysis,
        )
    )

    cleaned = clean_llm_string(response)

    return cleaned
