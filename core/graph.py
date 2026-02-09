#!/usr/bin/env python3
"""
This file:
1. Defines the execution flow
2. Connects nodes in the correct order
3. Uses LangGraph's state machine
4. Does NOT contain agent logic
"""

import logging

from langgraph.graph import StateGraph, END

from core.state import TutoringState, save_state_snapshot
from core.routing import task_executor
from core.planner_repair import validate_plan_schema, repair_plan, fallback_plan
from agents.multimodal.vision_agent import multimodal_vision_agent
from agents.planner.planner_agent import planner_agent

logger = logging.getLogger(__name__)


# -------------------------------------------------
# Graph node wrappers
# -------------------------------------------------

def multimodal_node(state: TutoringState):
    logger.info("Entering multimodal node")
    try:
        grounded = multimodal_vision_agent(
            image_base64=state.image_base64,
            user_profile=state.user_profile,
        )
        state.grounded_context = grounded
    except Exception as exc:
        logger.exception("Multimodal node failed, using empty grounded context: %s", exc)
    logger.info("Multimodal grounding complete")
    save_state_snapshot(state, "multimodal")
    return state


def planner_node(state: TutoringState, llm):
    logger.info("Entering planner node")
    try:
        plan = planner_agent(
            llm=llm,
            user_profile=state.user_profile,
            grounded_context=state.grounded_context,
        )
    except Exception as exc:
        logger.exception("Planner agent failed, using fallback plan: %s", exc)
        state.plan = fallback_plan(
            state.user_profile,
            state.grounded_context,
        )
        logger.info("Planning complete")
        return state
    try:
        validate_plan_schema(plan)
        state.plan = plan
    except Exception:
        # Planner failed -> repair or fallback
        try:
            repaired = repair_plan(plan)
            state.plan = repaired
        except Exception:
            state.plan = fallback_plan(
                state.user_profile,
                state.grounded_context,
            )
    logger.info("Planning complete")
    save_state_snapshot(state, "planner")
    return state


def executor_node(state: TutoringState, llm):
    logger.info("Entering executor node")
    updated = task_executor(llm=llm, state=state)
    save_state_snapshot(updated, "executor")
    return updated


# -------------------------------------------------
# Graph construction
# -------------------------------------------------

def build_graph(llm):
    logger.info("Building LangGraph pipeline")
    graph = StateGraph(TutoringState)

    graph.add_node("multimodal", lambda s: multimodal_node(s))
    graph.add_node("planner", lambda s: planner_node(s, llm))
    graph.add_node("executor", lambda s: executor_node(s, llm))

    graph.set_entry_point("multimodal")

    graph.add_edge("multimodal", "planner")
    graph.add_edge("planner", "executor")
    graph.add_edge("executor", END)

    return graph.compile()
