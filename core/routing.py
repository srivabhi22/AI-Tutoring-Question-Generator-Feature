#!/usr/bin/env python3
"""
This file:
1. Reads the planner output
2. Iterates through execution_order
3. Finds which agent should execute each task
4. Runs that agent
5. Stores outputs in state["knowledge_base"]
"""

# core/task_executor.py

from typing import Dict, Any
from core.state import TutoringState, UserProfile, PlannerOutput, GroundedContext
from config.agent_executor import AGENT_EXECUTORS


def task_executor(
    llm,
    state: TutoringState,
) -> TutoringState:
    """
    Executes planner-defined subtasks in the specified order.
    """

    plan = state["plan"]
    subtasks = {task["task_id"]: task for task in plan["subtasks"]}
    execution_order = plan["execution_order"]

    knowledge_base = state.get("knowledge_base", {})

    for task_id in execution_order:
        task = subtasks[task_id]
        agent_id = task["executed_by"]

        agent_fn = AGENT_EXECUTORS.get(agent_id)
        if agent_fn is None:
            raise RuntimeError(f"No executor found for agent: {agent_id}")

        output = agent_fn(
            llm=llm,
            task=task,
            state=state,
        )

        knowledge_base[task_id] = output

    state["knowledge_base"] = knowledge_base
    return state
