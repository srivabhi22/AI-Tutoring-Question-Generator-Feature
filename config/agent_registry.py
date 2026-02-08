#!/usr/bin/env python3
"""
This file defines what agents are allowed to exist in this system, and how are they identified?
"""
# ------------------------------------------------------------------
# Canonical list of allowed agent IDs
# ------------------------------------------------------------------

AVAILABLE_AGENTS = {
    "content_analyzer",
    "exam_pattern_analyst",
    "question_designer",
    "question_generator",
    "solver",
    "evaluator",
}


# ------------------------------------------------------------------
# Human-readable descriptions (for planner prompt, debugging)
# ------------------------------------------------------------------

AGENT_DESCRIPTIONS = {
    "content_analyzer": (
        "Extracts key concepts, definitions, facts, equations, "
        "chemical reactions, and relationships from the given content."
    ),

    "exam_pattern_analyst": (
        "Analyzes how the content is tested in the target exam, "
        "including question types, depth, weightage, and common pitfalls."
    ),

    "question_designer": (
        "Designs question intent, difficulty, and distractors "
        "without generating final questions."
    ),

    "question_generator": (
        "Generates final exam-aligned questions and model answers "
        "in structured JSON format."
    ),

    "solver": (
        "Solves generated questions step-by-step, including numerical "
        "and conceptual reasoning."
    ),

    "evaluator": (
        "Evaluates solutions using board- and exam-specific criteria "
        "and suggests improvements."
    ),
}
