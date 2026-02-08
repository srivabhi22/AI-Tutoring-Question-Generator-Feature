#!/usr/bin/env python3
"""
Maps agent IDs to their executable Python functions.
This is used ONLY at runtime by the task executor.
"""

from agents.analysis.content_analyzer import content_analyzer_agent
from agents.analysis.exam_pattern_analyst import exam_pattern_analyst_agent
from agents.design.question_designer import question_designer_agent
from agents.generation.question_generator import question_generator_agent
from agents.solving.solver_agent import solver_agent
from agents.evaluation.evaluator_agent import evaluator_agent


AGENT_EXECUTORS = {
    "content_analyzer": content_analyzer_agent,
    "exam_pattern_analyst": exam_pattern_analyst_agent,
    "question_designer": question_designer_agent,
    "question_generator": question_generator_agent,
    "solver": solver_agent,
    "evaluator": evaluator_agent,
}
