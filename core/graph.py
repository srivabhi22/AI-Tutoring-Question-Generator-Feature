#!/usr/bin/env python3
"""
This file:
1. Defines the execution flow
2. Connects nodes in the correct order
3. Uses LangGraph’s state machine
4. Does NOT contain agent logic
"""


from langgraph.graph import StateGraph, END

from core.state import TutoringState
from core.routing import task_executor
from core.planner_repair import validate_plan_schema, repair_plan, fallback_plan

from agents.multimodal.vision_agent import multimodal_vision_agent
from agents.planner.planner_agent import planner_agent
from agents.generation.question_generator import question_generator_agent
from agents.solving.solver_agent import solver_agent
from agents.evaluation.evaluator_agent import evaluator_agent


# -------------------------------------------------
# Graph node wrappers
# -------------------------------------------------

def multimodal_node(state: TutoringState):
    grounded = multimodal_vision_agent(
        image_base64=state["image_base64"],
        user_profile=state["user_profile"],
    )
    state["grounded_context"] = grounded
    return state


def planner_node(state: TutoringState, llm):
    plan = planner_agent(
        llm=llm,
        user_profile=state["user_profile"],
        grounded_context=state["grounded_context"],
    )
    try:
        validate_plan_schema(plan)
        state["plan"] = plan

    except Exception:
        # Planner failed → repair or fallback
        try:
            repaired = repair_plan(plan)
            state["plan"] = repaired
        except Exception:
            state["plan"] = fallback_plan(
                state["user_profile"],
                state["grounded_context"],
            )

    return state


def executor_node(state: TutoringState, llm):
    return task_executor(llm=llm, state=state)


def generator_node(state: TutoringState, llm):
    # Find generator task
    for task in state["plan"]["subtasks"]:
        if task["executed_by"] == "question_generator":
            state["question_bank"] = question_generator_agent(
                llm=llm,
                task=task,
                state=state,
            )
            break
    return state


def solver_node(state: TutoringState, llm):
    for task in state["plan"]["subtasks"]:
        if task["executed_by"] == "solver":
            state["solver_output"] = solver_agent(
                llm=llm,
                task=task,
                state=state,
            )
            break
    return state


def evaluator_node(state: TutoringState, llm):
    for task in state["plan"]["subtasks"]:
        if task["executed_by"] == "evaluator":
            state["evaluation"] = evaluator_agent(
                llm=llm,
                task=task,
                state=state,
            )
            break
    return state


# -------------------------------------------------
# Graph construction
# -------------------------------------------------

def build_graph(llm):
    graph = StateGraph(TutoringState)

    graph.add_node("multimodal", lambda s: multimodal_node(s))
    graph.add_node("planner", lambda s: planner_node(s, llm))
    graph.add_node("executor", lambda s: executor_node(s, llm))
    graph.add_node("generator", lambda s: generator_node(s, llm))
    graph.add_node("solver", lambda s: solver_node(s, llm))
    graph.add_node("evaluator", lambda s: evaluator_node(s, llm))

    graph.set_entry_point("multimodal")

    graph.add_edge("multimodal", "planner")
    graph.add_edge("planner", "executor")
    graph.add_edge("executor", "generator")
    graph.add_edge("generator", "solver")
    graph.add_edge("solver", "evaluator")
    graph.add_edge("evaluator", END)

    return graph.compile()
