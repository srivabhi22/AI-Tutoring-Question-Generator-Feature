import pytest

from core.graph import _normalize_plan_task_ids
from core.routing import task_executor
from core.state import PlannerOutput, TutoringState, UserProfile
from config import agent_executor


def test_normalize_plan_rejects_duplicate_agents():
    plan = PlannerOutput(
        planning_context={},
        objective="test",
        subtasks=[
            {
                "task_id": "t1",
                "purpose": "A",
                "expected_output": "A",
                "priority": "High",
                "executed_by": "content_analyzer",
            },
            {
                "task_id": "t2",
                "purpose": "B",
                "expected_output": "B",
                "priority": "High",
                "executed_by": "content_analyzer",
            },
        ],
        execution_order=["t1", "t2"],
    )

    with pytest.raises(ValueError):
        _normalize_plan_task_ids(plan)


def test_agent_fallback_on_failure(monkeypatch):
    def failing_agent(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setitem(agent_executor.AGENT_EXECUTORS, "content_analyzer", failing_agent)

    plan = PlannerOutput(
        planning_context={},
        objective="test",
        subtasks=[
            {
                "task_id": "content_analyzer",
                "purpose": "Extract",
                "expected_output": "Extracted content",
                "priority": "High",
                "executed_by": "content_analyzer",
            }
        ],
        execution_order=["content_analyzer"],
    )

    state = TutoringState(
        user_profile=UserProfile(class_level="11", board="CBSE", target_exam="NEET"),
        image_base64="dummy",
        plan=plan,
    )

    updated = task_executor(llm=None, state=state)
    assert "content_analyzer" in updated.knowledge_base
    assert "agent:content_analyzer" in updated.run_diagnostics.get("fallbacks", [])
