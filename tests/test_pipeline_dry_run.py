from core.graph import build_graph
from core.state import TutoringState, UserProfile, GroundedContext, PlannerOutput, ensure_state
from config import agent_executor


def test_pipeline_dry_run(monkeypatch):
    def fake_multimodal(*args, **kwargs):
        return GroundedContext(
            metadata={
                "subject": "Chemistry",
                "chapter": "Test Chapter",
                "sub_topic": "Test Topic",
            },
            image_analysis="Dummy image analysis",
        )

    def fake_planner(*args, **kwargs):
        return PlannerOutput(
            planning_context={
                "class": "11",
                "board": "CBSE",
                "target_exam": "NEET",
                "subject": "Chemistry",
                "chapter": "Test Chapter",
                "sub_topic": "Test Topic",
            },
            objective="generate_exam_aligned_questions",
            subtasks=[
                {
                    "task_id": "extract",
                    "purpose": "Extract",
                    "expected_output": "Extracted content",
                    "priority": "High",
                    "executed_by": "content_analyzer",
                },
                {
                    "task_id": "analyze_exam",
                    "purpose": "Analyze",
                    "expected_output": "Exam analysis",
                    "priority": "High",
                    "executed_by": "exam_pattern_analyst",
                },
                {
                    "task_id": "design_questions",
                    "purpose": "Design",
                    "expected_output": "Design guidance",
                    "priority": "Medium",
                    "executed_by": "question_designer",
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
            execution_order=[
                "extract",
                "analyze_exam",
                "design_questions",
                "generate",
                "solve",
                "evaluate",
            ],
        )

    def fake_content_analyzer(*args, **kwargs):
        return {"knowledge_base": {"extract": "concepts"}}

    def fake_exam_analyst(*args, **kwargs):
        return {"knowledge_base": {"analyze_exam": "patterns"}}

    def fake_designer(*args, **kwargs):
        return {"knowledge_base": {"design_questions": "designs"}}

    def fake_generator(*args, **kwargs):
        return {
            "question_bank": {"mcq": [{"q": "Dummy", "answer": "A"}]},
            "knowledge_base": {"generate": "questions"},
        }

    def fake_solver(*args, **kwargs):
        return {
            "solver_output": {"mcq": [{"q": "Dummy", "solution": "Solved"}]},
            "knowledge_base": {"solve": "solutions"},
        }

    def fake_evaluator(*args, **kwargs):
        return {
            "evaluation": {"overall_feedback": "OK"},
            "knowledge_base": {"evaluate": "evaluation"},
        }

    monkeypatch.setattr("core.graph.multimodal_vision_agent", fake_multimodal)
    monkeypatch.setattr("core.graph.planner_agent", fake_planner)

    monkeypatch.setitem(agent_executor.AGENT_EXECUTORS, "content_analyzer", fake_content_analyzer)
    monkeypatch.setitem(agent_executor.AGENT_EXECUTORS, "exam_pattern_analyst", fake_exam_analyst)
    monkeypatch.setitem(agent_executor.AGENT_EXECUTORS, "question_designer", fake_designer)
    monkeypatch.setitem(agent_executor.AGENT_EXECUTORS, "question_generator", fake_generator)
    monkeypatch.setitem(agent_executor.AGENT_EXECUTORS, "solver", fake_solver)
    monkeypatch.setitem(agent_executor.AGENT_EXECUTORS, "evaluator", fake_evaluator)

    graph = build_graph(None)

    initial_state = TutoringState(
        user_profile=UserProfile(
            class_level="11",
            board="CBSE",
            target_exam="NEET",
        ),
        image_base64="DUMMY_IMAGE",
    )

    final_state = ensure_state(graph.invoke(initial_state))

    assert final_state.grounded_context.metadata["subject"] == "Chemistry"
    assert "generate" in final_state.knowledge_base
    assert "solve" in final_state.knowledge_base
    assert "evaluate" in final_state.knowledge_base
    assert "mcq" in final_state.question_bank
    assert "mcq" in final_state.solver_output
