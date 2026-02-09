#!/usr/bin/env python3
"""
This file:
1. Load the LLM
2. Prepare initial state
3. Run the LangGraph
4. Return the final output (question bank + evaluation)
"""

# main.py

import logging

from core.graph import build_graph
from core.logging_config import configure_logging
from core.llm_loader import load_text_llm

# -------------------------------------------------
# LLM SETUP (example: Gemini / OpenAI / Claude)
# -------------------------------------------------

# IMPORTANT:
# Replace this with the LLM you are actually using.


from core.state import TutoringState, UserProfile, ensure_state

logger = logging.getLogger(__name__)


# -------------------------------------------------
# Image loader (base64)
# -------------------------------------------------

import base64

def load_image_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# -------------------------------------------------
# Main execution
# -------------------------------------------------

def run_pipeline(
    image_path: str,
    class_level: str,
    board: str,
    target_exam: str,
):
    configure_logging()
    logger.info("Starting pipeline run")
    llm = load_text_llm()
    graph = build_graph(llm)

    # Initialize state (Pydantic handles defaults)
    initial_state = TutoringState(
        user_profile=UserProfile(
            class_level=class_level,
            board=board,
            target_exam=target_exam,
        ),
        image_base64=load_image_base64(image_path),
    )

    # Run workflow
    final_state: TutoringState = ensure_state(graph.invoke(initial_state))

    logger.info("Pipeline run complete")
    return {
        "questions": final_state.question_bank,
        "solutions": final_state.solver_output,
        "evaluation": final_state.evaluation,
    }


# -------------------------------------------------
# Example usage
# -------------------------------------------------

if __name__ == "__main__":
    result = run_pipeline(
        image_path=r"C:\Users\HP\PycharmProjects\AI-Tutoring-Question-Generator-Feature\data.png",
        class_level="11",
        board="CBSE",
        target_exam="NEET",
    )

    print("\n=== QUESTION BANK ===\n")
    print(result["questions"])

    print("\n=== SOLUTIONS ===\n")
    print(result["solutions"])

    print("\n=== EVALUATION ===\n")
    print(result["evaluation"])
