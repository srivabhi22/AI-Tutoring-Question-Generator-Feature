def test_all_imports():
    # Core
    from core.state import TutoringState, UserProfile
    from core.graph import build_graph
    from core.llm_loader import load_text_llm

    # Agents
    from agents.multimodal.vision_agent import multimodal_vision_agent
    from agents.planner.planner_agent import planner_agent
    from agents.solving.solver_agent import solver_agent
    from agents.analysis.content_analyzer import content_analyzer_agent
    from agents.analysis.exam_pattern_analyst import exam_pattern_analyst_agent
    from agents.design.question_designer import question_designer_agent
    from agents.generation.question_generator import question_generator_agent
    from agents.solving.solver_agent import solver_agent
    from agents.evaluation.evaluator_agent import evaluator_agent

    # Tools
    from tools.math_solver import python_math
    # Interfaces
    from interfaces.api import app

    assert True
