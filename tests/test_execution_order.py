from core.graph import build_graph
from core.state import TutoringState, UserProfile, GroundedContext, PlannerOutput
from config import agent_executor


def test_execution_order(monkeypatch):
    execution_trace = []

    def fake_multimodal(*args, **kwargs):
        execution_trace.append("multimodal")
        return GroundedContext(
            metadata={"subject": "Test", "chapter": "Test", "sub_topic": "Test"},
            image_analysis="Test",
        )

    def fake_planner(*args, **kwargs):
        execution_trace.append("planner")
        return PlannerOutput(
            planning_context={
                "class": "11",
                "board": "CBSE",
                "target_exam": "NEET",
                "subject": "Test",
                "chapter": "Test",
                "sub_topic": "Test",
            },
            objective="test",
            subtasks=[
                {
                    "task_id": "extract",
                    "purpose": "Extract",
                    "expected_output": "Extracted content",
                    "priority": "High",
                    "executed_by": "content_analyzer",
                },
                {
                    "task_id": "generate",
                    "purpose": "Generate",
                    "expected_output": "Questions",
                    "priority": "High",
                    "executed_by": "question_generator",
                },
                {
                    "task_id": "solve",
                    "purpose": "Solve",
                    "expected_output": "Solutions",
                    "priority": "High",
                    "executed_by": "solver",
                },
                {
                    "task_id": "evaluate",
                    "purpose": "Evaluate",
                    "expected_output": "Evaluation",
                    "priority": "High",
                    "executed_by": "evaluator",
                },
            ],
            execution_order=["extract", "generate", "solve", "evaluate"],
        )

    def fake_content_analyzer(*args, **kwargs):
        execution_trace.append("content_analyzer")
        return {"knowledge_base": {"extract": "content"}}

    def fake_generator(*args, **kwargs):
        execution_trace.append("question_generator")
        return {"question_bank": {"mcq": []}, "knowledge_base": {"generate": "qb"}}

    def fake_solver(*args, **kwargs):
        execution_trace.append("solver")
        return {"solver_output": {"mcq": []}, "knowledge_base": {"solve": "sol"}}

    def fake_evaluator(*args, **kwargs):
        execution_trace.append("evaluator")
        return {"evaluation": {"overall": "ok"}, "knowledge_base": {"evaluate": "eval"}}

    monkeypatch.setattr("core.graph.multimodal_vision_agent", fake_multimodal)
    monkeypatch.setattr("core.graph.planner_agent", fake_planner)

    monkeypatch.setitem(agent_executor.AGENT_EXECUTORS, "content_analyzer", fake_content_analyzer)
    monkeypatch.setitem(agent_executor.AGENT_EXECUTORS, "question_generator", fake_generator)
    monkeypatch.setitem(agent_executor.AGENT_EXECUTORS, "solver", fake_solver)
    monkeypatch.setitem(agent_executor.AGENT_EXECUTORS, "evaluator", fake_evaluator)

    graph = build_graph(None)

    state = TutoringState(
        user_profile=UserProfile(
            class_level="11",
            board="CBSE",
            target_exam="NEET",
        ),
        image_base64="dummy",
    )

    graph.invoke(state)

    assert execution_trace == [
        "multimodal",
        "planner",
        "content_analyzer",
        "question_generator",
        "solver",
        "evaluator",
    ]
