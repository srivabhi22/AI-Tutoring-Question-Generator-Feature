#!/usr/bin/env python3
"""
Plan validation, repair, and fallback logic.
"""

import logging
from typing import Dict, Any, List

from pydantic import BaseModel

from config.agent_registry import AVAILABLE_AGENTS
from core.state import PlannerOutput, UserProfile, GroundedContext

logger = logging.getLogger(__name__)


def _model_to_dict(plan: Any) -> Dict[str, Any]:
    if isinstance(plan, BaseModel):
        if hasattr(plan, "model_dump"):
            return plan.model_dump()
        return plan.dict()
    if isinstance(plan, dict):
        return plan
    raise TypeError(f"Unsupported plan type: {type(plan)}")


# -------------------------------------------------
# Validation
# -------------------------------------------------

def validate_plan_schema(plan: PlannerOutput) -> None:
    required_top_keys = {
        "planning_context",
        "objective",
        "subtasks",
        "execution_order",
    }

    plan_dict = _model_to_dict(plan)

    if set(plan_dict.keys()) != required_top_keys:
        raise ValueError("Planner output has invalid top-level keys")

    if not isinstance(plan_dict["subtasks"], list):
        raise ValueError("subtasks must be a list")

    if not isinstance(plan_dict["execution_order"], list):
        raise ValueError("execution_order must be a list")

    task_ids = set()

    for task in plan_dict["subtasks"]:
        for field in ["task_id", "purpose", "expected_output", "priority", "executed_by"]:
            if field not in task:
                raise ValueError(f"Task missing required field: {field}")

        agent = task["executed_by"]
        if agent not in AVAILABLE_AGENTS:
            raise ValueError(f"Invalid agent ID: {agent}")

        task_ids.add(task["task_id"])

    for tid in plan_dict["execution_order"]:
        if tid not in task_ids:
            raise ValueError(f"execution_order references unknown task_id: {tid}")


# -------------------------------------------------
# Repair logic
# -------------------------------------------------

_AGENT_REPAIR_MAP = {
    "content analyzer": "content_analyzer",
    "content_analyzer_agent": "content_analyzer",
    "concept extractor": "content_analyzer",
    "exam analyst": "exam_pattern_analyst",
    "exam pattern agent": "exam_pattern_analyst",
    "question designer agent": "question_designer",
    "distractor agent": "question_designer",
    "generator": "question_generator",
    "question writer": "question_generator",
    "solution agent": "solver",
    "answer solver": "solver",
    "teacher": "evaluator",
    "examiner": "evaluator",
}


def repair_plan(plan: PlannerOutput) -> PlannerOutput:
    plan_dict = _model_to_dict(plan)
    repaired_tasks: List[Dict[str, Any]] = []

    for task in plan_dict.get("subtasks", []):
        agent = str(task.get("executed_by", "")).lower().strip()

        if agent not in AVAILABLE_AGENTS:
            agent = _AGENT_REPAIR_MAP.get(agent, agent)

        if agent not in AVAILABLE_AGENTS:
            # Heuristic fallback based on task_id keywords
            tid = str(task.get("task_id", "")).lower()
            if "extract" in tid or "analy" in tid:
                agent = "content_analyzer"
            elif "exam" in tid:
                agent = "exam_pattern_analyst"
            elif "design" in tid:
                agent = "question_designer"
            elif "generate" in tid:
                agent = "question_generator"
            elif "solve" in tid:
                agent = "solver"
            else:
                agent = "evaluator"

        task["executed_by"] = agent
        repaired_tasks.append(task)

    plan_dict["subtasks"] = repaired_tasks

    # Repair execution order
    valid_ids = [t["task_id"] for t in repaired_tasks]
    plan_dict["execution_order"] = [
        tid for tid in plan_dict.get("execution_order", []) if tid in valid_ids
    ]

    if not plan_dict["execution_order"]:
        plan_dict["execution_order"] = valid_ids

    logger.warning("Planner output repaired")
    return PlannerOutput(**plan_dict)


# -------------------------------------------------
# Fallback plan (guaranteed minimal plan)
# -------------------------------------------------

def fallback_plan(
    user_profile: UserProfile,
    grounded_context: GroundedContext,
) -> PlannerOutput:
    meta = grounded_context.metadata

    return PlannerOutput(
        planning_context={
            "class": user_profile.class_level,
            "board": user_profile.board,
            "target_exam": user_profile.target_exam,
            "subject": meta.get("subject", ""),
            "chapter": meta.get("chapter", ""),
            "sub_topic": meta.get("sub_topic", ""),
        },
        objective="generate_exam_aligned_questions",
        subtasks=[
            {
                "task_id": "extract_core_content",
                "purpose": "Extract key concepts and facts",
                "expected_output": "Structured list of concepts and facts",
                "priority": "High",
                "executed_by": "content_analyzer",
            },
            {
                "task_id": "analyze_exam_alignment",
                "purpose": "Identify exam relevance and question styles",
                "expected_output": "Exam-aligned insights",
                "priority": "High",
                "executed_by": "exam_pattern_analyst",
            },
            {
                "task_id": "generate_questions",
                "purpose": "Generate final questions and answers",
                "expected_output": "Structured question bank",
                "priority": "High",
                "executed_by": "question_generator",
            },
        ],
        execution_order=[
            "extract_core_content",
            "analyze_exam_alignment",
            "generate_questions",
        ],
    )
