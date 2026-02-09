import pytest

from core.planner_repair import validate_plan_schema, repair_plan
from core.state import PlannerOutput


def test_validate_plan_schema_accepts_valid_plan():
    plan = PlannerOutput(
        planning_context={
            "class": "11",
            "board": "CBSE",
            "target_exam": "NEET",
            "subject": "Chemistry",
            "chapter": "Test",
            "sub_topic": "Test",
        },
        objective="generate_exam_aligned_questions",
        subtasks=[
            {
                "task_id": "extract",
                "purpose": "Extract",
                "expected_output": "Extracted content",
                "priority": "High",
                "executed_by": "content_analyzer",
            }
        ],
        execution_order=["extract"],
    )

    validate_plan_schema(plan)


def test_validate_plan_schema_rejects_invalid_agent():
    bad_plan = {
        "planning_context": {},
        "objective": "test",
        "subtasks": [
            {
                "task_id": "extract",
                "purpose": "Extract",
                "expected_output": "Output",
                "priority": "High",
                "executed_by": "unknown_agent",
            }
        ],
        "execution_order": ["extract"],
    }

    with pytest.raises(ValueError):
        validate_plan_schema(bad_plan)


def test_repair_plan_normalizes_agent_ids():
    plan = PlannerOutput(
        planning_context={},
        objective="test",
        subtasks=[
            {
                "task_id": "extract",
                "purpose": "Extract",
                "expected_output": "Output",
                "priority": "High",
                "executed_by": "content analyzer",
            }
        ],
        execution_order=["extract"],
    )

    repaired = repair_plan(plan)
    assert repaired.subtasks[0]["executed_by"] == "content_analyzer"
