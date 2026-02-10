#!/usr/bin/env python3
"""
Executes planner-defined subtasks in order and updates the shared state.
"""

import logging
from typing import Dict, Any

from core.state import TutoringState, save_state_snapshot
from core.resilience import run_with_retry
from config.resilience import AGENT_RETRIES, AGENT_TIMEOUT_SEC, PIPELINE_RETRY_DELAY_SEC
from config.agent_executor import AGENT_EXECUTORS

logger = logging.getLogger(__name__)


def _record_diagnostic(state: TutoringState, meta: Dict[str, Any]) -> None:
    diagnostics = state.run_diagnostics
    diagnostics["events"].append(meta)
    if meta.get("fallback_used"):
        diagnostics["fallbacks"].append(meta.get("label"))
    label = meta.get("label")
    if label:
        diagnostics["retries"][label] = meta.get("attempts", 1) - 1
        diagnostics["timings_ms"][label] = meta.get("duration_ms", 0)


def _agent_fallback(agent_id: str) -> Dict[str, Any]:
    if agent_id == "content_analyzer":
        return {"knowledge_base": {agent_id: ""}}
    if agent_id == "exam_pattern_analyst":
        return {"knowledge_base": {agent_id: ""}}
    if agent_id == "question_designer":
        return {"knowledge_base": {agent_id: ""}}
    if agent_id == "question_generator":
        return {
            "question_bank": {"mcq": [], "short_answer": [], "long_answer": []},
            "knowledge_base": {agent_id: {"mcq": [], "short_answer": [], "long_answer": []}},
        }
    if agent_id == "solver":
        return {
            "solver_output": {"mcq": [], "short_answer": [], "long_answer": []},
            "knowledge_base": {agent_id: {"mcq": [], "short_answer": [], "long_answer": []}},
        }
    if agent_id == "evaluator":
        return {
            "evaluation": {
                "overall_feedback": "Evaluator unavailable; fallback applied.",
                "mcq": [],
                "short_answer": [],
                "long_answer": [],
            },
            "knowledge_base": {agent_id: {
                "overall_feedback": "Evaluator unavailable; fallback applied.",
                "mcq": [],
                "short_answer": [],
                "long_answer": [],
            }},
        }
    return {"knowledge_base": {agent_id: ""}}


def _count_sections(payload: Any) -> Dict[str, int]:
    if not isinstance(payload, dict):
        return {}
    counts = {}
    for key in ("mcq", "short_answer", "long_answer"):
        value = payload.get(key)
        counts[key] = len(value) if isinstance(value, list) else 0
    return counts


def _merge_knowledge_base(
    state: TutoringState,
    update: Dict[str, Any],
    agent_id: str,
) -> None:
    if not isinstance(update, dict):
        raise TypeError("knowledge_base update must be a dict")
    if agent_id in update:
        state.knowledge_base[agent_id] = update[agent_id]
        return
    if len(update) == 1:
        state.knowledge_base[agent_id] = next(iter(update.values()))
        return
    state.knowledge_base[agent_id] = update


def _normalize_state_field(key: str, value: Any) -> Any:
    if key == "question_bank":
        if isinstance(value, list):
            return {"mcq": value, "short_answer": [], "long_answer": []}
        if not isinstance(value, dict):
            return {"mcq": [], "short_answer": [], "long_answer": []}
    if key == "solver_output":
        if isinstance(value, list):
            return {"mcq": value, "short_answer": [], "long_answer": []}
        if not isinstance(value, dict):
            return {"mcq": [], "short_answer": [], "long_answer": []}
    if key == "evaluation":
        if isinstance(value, list):
            return {
                "overall_feedback": "Evaluator returned a list; wrapped for safety.",
                "mcq": value,
                "short_answer": [],
                "long_answer": [],
            }
        if not isinstance(value, dict):
            return {
                "overall_feedback": "Evaluator output was not a dict; coerced.",
                "mcq": [],
                "short_answer": [],
                "long_answer": [],
            }
    return value


def task_executor(
    llm,
    state: TutoringState,
) -> TutoringState:
    """
    Executes planner-defined subtasks in the specified order.
    """
    plan = state.plan
    subtasks = {task["task_id"]: task for task in plan.subtasks}
    execution_order = plan.execution_order

    logger.info("Executing %d tasks", len(execution_order))

    for task_id in execution_order:
        task = subtasks.get(task_id)
        if task is None:
            logger.warning("Skipping unknown task_id: %s", task_id)
            continue

        agent_id = task.get("executed_by")
        agent_fn = AGENT_EXECUTORS.get(agent_id)
        if agent_fn is None:
            raise RuntimeError(f"No executor found for agent: {agent_id}")

        logger.info("Running task %s with agent %s", task_id, agent_id)
        def _run():
            return agent_fn(
                llm=llm,
                task=task,
                state=state,
            )

        def _fallback(_exc: Exception):
            return _agent_fallback(agent_id)

        agent_update, meta = run_with_retry(
            f"agent:{agent_id}",
            _run,
            retries=AGENT_RETRIES,
            delay_sec=PIPELINE_RETRY_DELAY_SEC,
            timeout_sec=AGENT_TIMEOUT_SEC,
            fallback=_fallback,
        )
        _record_diagnostic(state, meta)

        if not isinstance(agent_update, dict):
            logger.warning(
                "Agent '%s' returned non-dict output: %s; using fallback",
                agent_id,
                type(agent_update),
            )
            agent_update = _agent_fallback(agent_id)
            state.run_diagnostics["fallbacks"].append(f"agent:{agent_id}")

        # Merge state updates
        for key, value in agent_update.items():
            if key == "knowledge_base":
                _merge_knowledge_base(state, value, agent_id)
            elif hasattr(state, key):
                normalized = _normalize_state_field(key, value)
                setattr(state, key, normalized)
            else:
                logger.warning("Ignoring unknown state field: %s", key)

        output_counts = {}
        if "question_bank" in agent_update:
            output_counts["question_bank"] = _count_sections(agent_update.get("question_bank"))
        if "solver_output" in agent_update:
            output_counts["solver_output"] = _count_sections(agent_update.get("solver_output"))
        if "evaluation" in agent_update:
            output_counts["evaluation"] = _count_sections(agent_update.get("evaluation"))
        if output_counts:
            state.run_diagnostics["output_counts"][agent_id] = output_counts

        logger.info("Completed task %s", task_id)
        save_state_snapshot(state, f"task:{task_id}")

    logger.info("Task execution complete")
    return state
