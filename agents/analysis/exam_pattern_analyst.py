#!/usr/bin/env python3
"""
This agent answers:
Given the extracted content, how is this usually tested in the target exam?
"""



from typing import Dict, Any

from preprocessing.text_cleaner import clean_llm_string


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
Class: {planning_context["class"]}
Board: {planning_context["board"]}
Target Exam: {planning_context["target_exam"]}
Subject: {planning_context["subject"]}
Chapter: {planning_context["chapter"]}
Sub-topic: {planning_context["sub_topic"]}

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
    state: Dict[str, Any],
) -> str:
    """
    Analyzes exam relevance and testing patterns for extracted content.
    """

    planning_context = state["plan"]["planning_context"]

    # Get output from content analyzer
    extracted_content = ""
    for key, value in state["knowledge_base"].items():
        if "extract" in key or "content" in key:
            extracted_content = value
            break

    response = llm.invoke(
        build_exam_pattern_prompt(task, planning_context, extracted_content)
    )

    cleaned = clean_llm_string(response)

    return cleaned
