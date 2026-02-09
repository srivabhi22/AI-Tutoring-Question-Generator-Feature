#!/usr/bin/env python3
"""
This file defines what information exists in the system at any point in time.
(Pydantic-based state schema for LangGraph)
"""

from typing import Dict, List, Any
import json
import os
from datetime import datetime, timezone
from pydantic import BaseModel, Field


# -------------------------------------------------
# User Profile
# -------------------------------------------------

class UserProfile(BaseModel):
    class_level: str        # e.g. "11", "12"
    board: str              # e.g. "CBSE"
    target_exam: str        # e.g. "NEET"


# -------------------------------------------------
# Multimodal Grounding Output
# -------------------------------------------------

class GroundedContext(BaseModel):
    metadata: Dict[str, str] = Field(default_factory=dict)
    image_analysis: str = ""


# -------------------------------------------------
# Planner Output
# -------------------------------------------------

class PlannerOutput(BaseModel):
    planning_context: Dict[str, str] = Field(default_factory=dict)
    objective: str = ""
    subtasks: List[Dict[str, Any]] = Field(default_factory=list)
    execution_order: List[str] = Field(default_factory=list)


# -------------------------------------------------
# Global Tutoring State
# -------------------------------------------------

class TutoringState(BaseModel):
    # ---- User Input ----
    user_profile: UserProfile
    image_base64: str

    # ---- Multimodal Output ----
    grounded_context: GroundedContext = Field(default_factory=GroundedContext)

    # ---- Planner Output ----
    plan: PlannerOutput = Field(default_factory=PlannerOutput)

    # ---- Intermediate Knowledge ----
    knowledge_base: Dict[str, Any] = Field(default_factory=dict)

    # ---- Final Outputs ----
    question_bank: Dict[str, Any] = Field(default_factory=dict)
    solver_output: Dict[str, Any] = Field(default_factory=dict)
    evaluation: Dict[str, Any] = Field(default_factory=dict)


def ensure_state(value: Any) -> "TutoringState":
    if isinstance(value, TutoringState):
        return value
    if isinstance(value, dict):
        return TutoringState(**value)
    raise TypeError(f"Unsupported state type: {type(value)}")


def save_state_snapshot(
    state: "TutoringState",
    stage: str,
    *,
    output_dir: str = "logs",
    redact_image: bool = True,
) -> str:
    data = state.model_dump()
    if redact_image:
        data["image_base64"] = "[redacted]"

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stage": stage,
        "state": data,
    }

    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "state.jsonl")
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
    return path
