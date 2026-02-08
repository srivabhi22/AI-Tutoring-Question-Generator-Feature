#!/usr/bin/env python3
"""
This agent answers:
From the grounded content, what are the core concepts, facts, definitions,
equations, reactions, and relationships?
"""

# agents/analysis/content_analyzer.py

from typing import Dict, Any

from preprocessing.text_cleaner import clean_llm_string


def build_content_analyzer_prompt(
    task: Dict[str, Any],
    planning_context: Dict[str, str],
    grounded_context: Dict[str, Any],
) -> str:
    return f"""
You are a content analysis agent.

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

SOURCE CONTENT (CLEANED IMAGE ANALYSIS):
{grounded_context["image_analysis"]}

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
    state: Dict[str, Any],
) -> str:
    """
    Extracts core academic content from the grounded context.
    """

    planning_context = state["plan"]["planning_context"]
    grounded_context = state["grounded_context"]

    response = llm.invoke(
        build_content_analyzer_prompt(task, planning_context, grounded_context)
    )

    # Clean text output
    cleaned = clean_llm_string(response)

    return cleaned
