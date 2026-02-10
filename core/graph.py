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

from core.state import TutoringState, save_state_snapshot, GroundedContext
from core.routing import task_executor
from core.resilience import run_with_retry
from core.planner_repair import validate_plan_schema, repair_plan, fallback_plan
from config.resilience import NODE_RETRIES, NODE_TIMEOUT_SEC, PIPELINE_RETRY_DELAY_SEC
from agents.multimodal.vision_agent import multimodal_vision_agent
from agents.planner.planner_agent import planner_agent

logger = logging.getLogger(__name__)

def _record_diagnostic(state: TutoringState, meta: dict) -> None:
    diagnostics = state.run_diagnostics
    diagnostics["events"].append(meta)
    if meta.get("fallback_used"):
        diagnostics["fallbacks"].append(meta.get("label"))
    label = meta.get("label")
    if label:
        diagnostics["retries"][label] = meta.get("attempts", 1) - 1
        diagnostics["timings_ms"][label] = meta.get("duration_ms", 0)


def _normalize_plan_task_ids(plan):
    seen_agents = set()
    for task in plan.subtasks:
        agent_id = task.get("executed_by")
        if not agent_id:
            raise ValueError("Planner task missing executed_by")
        if agent_id in seen_agents:
            raise ValueError(f"Duplicate agent task not allowed: {agent_id}")
        seen_agents.add(agent_id)

    subtasks = {task["task_id"]: task for task in plan.subtasks}
    normalized_order = []
    seen = set()
    for task_id in plan.execution_order:
        task = subtasks.get(task_id)
        if task is None:
            continue
        agent_id = task.get("executed_by")
        if not agent_id:
            raise ValueError("Planner task missing executed_by")
        task["task_id"] = agent_id
        if agent_id in seen:
            continue
        normalized_order.append(agent_id)
        seen.add(agent_id)
    plan.execution_order = normalized_order
    return plan


# -------------------------------------------------
# Graph node wrappers
# -------------------------------------------------

def multimodal_node(state: TutoringState):
    logger.info("Entering multimodal node")
    def _run():
        return multimodal_vision_agent(
            image_base64=state.image_base64,
            user_profile=state.user_profile,
        )

    def _fallback(_exc: Exception):
        return GroundedContext()

    grounded, meta = run_with_retry(
        "multimodal",
        _run,
        retries=NODE_RETRIES.get("multimodal", 0),
        delay_sec=PIPELINE_RETRY_DELAY_SEC,
        timeout_sec=NODE_TIMEOUT_SEC.get("multimodal"),
        fallback=_fallback,
    )
    state.grounded_context = grounded
    _record_diagnostic(state, meta)
    logger.info("Multimodal grounding complete")
    save_state_snapshot(state, "multimodal")
    return state


def planner_node(state: TutoringState, llm):
    logger.info("Entering planner node")
    def _run():
        return planner_agent(
            llm=llm,
            user_profile=state.user_profile,
            grounded_context=state.grounded_context,
        )

    def _fallback(_exc: Exception):
        return fallback_plan(
            state.user_profile,
            state.grounded_context,
        )

    plan, meta = run_with_retry(
        "planner",
        _run,
        retries=NODE_RETRIES.get("planner", 0),
        delay_sec=PIPELINE_RETRY_DELAY_SEC,
        timeout_sec=NODE_TIMEOUT_SEC.get("planner"),
        fallback=_fallback,
    )
    _record_diagnostic(state, meta)
    try:
        validate_plan_schema(plan)
        state.plan = _normalize_plan_task_ids(plan)
    except Exception:
        # Planner failed -> repair or fallback
        try:
            repaired = repair_plan(plan)
            state.plan = _normalize_plan_task_ids(repaired)
        except Exception:
            fallback = fallback_plan(
                state.user_profile,
                state.grounded_context,
            )
            state.plan = _normalize_plan_task_ids(fallback)
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
