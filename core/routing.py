#!/usr/bin/env python3
"""
Executes planner-defined subtasks in order and updates the shared state.
"""

import logging
from typing import Dict, Any

from core.state import TutoringState, save_state_snapshot
from config.agent_executor import AGENT_EXECUTORS

logger = logging.getLogger(__name__)


def _merge_knowledge_base(state: TutoringState, update: Dict[str, Any]) -> None:
    if not isinstance(update, dict):
        raise TypeError("knowledge_base update must be a dict")
    state.knowledge_base.update(update)


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
        agent_update = agent_fn(
            llm=llm,
            task=task,
            state=state,
        )

        if not isinstance(agent_update, dict):
            raise TypeError(
                f"Agent '{agent_id}' returned non-dict output: {type(agent_update)}"
            )

        # Merge state updates
        for key, value in agent_update.items():
            if key == "knowledge_base":
                _merge_knowledge_base(state, value)
            elif hasattr(state, key):
                normalized = _normalize_state_field(key, value)
                setattr(state, key, normalized)
            else:
                logger.warning("Ignoring unknown state field: %s", key)

        # Ensure each task is tracked in the knowledge base for traceability
        if task_id not in state.knowledge_base:
            state.knowledge_base[task_id] = {"agent": agent_id, "output": agent_update}

        logger.info("Completed task %s", task_id)
        save_state_snapshot(state, f"task:{task_id}")

    logger.info("Task execution complete")
    return state
