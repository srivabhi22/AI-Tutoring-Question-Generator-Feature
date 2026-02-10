#!/usr/bin/env python3
"""
FastAPI interface for the tutoring pipeline.
"""

import base64
import logging
from typing import Optional, Dict, Any

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field

from core.graph import build_graph
from core.llm_loader import load_text_llm
from core.state import TutoringState, UserProfile, ensure_state
from core.logging_config import configure_logging
from config.api import MAX_IMAGE_BYTES, ALLOWED_IMAGE_TYPES, MAX_FIELD_LENGTH

logger = logging.getLogger(__name__)

app = FastAPI(title="AI Tutoring Question Generator", version="1.0.0")


class GenerateRequest(BaseModel):
    image_base64: str = Field(..., min_length=1)
    class_level: str = Field(..., min_length=1)
    board: str = Field(..., min_length=1)
    target_exam: str = Field(..., min_length=1)


class GenerateResponse(BaseModel):
    questions: Dict[str, Any]
    solutions: Dict[str, Any]
    evaluation: Dict[str, Any]
    diagnostics: Dict[str, Any] = Field(default_factory=dict)


class Pipeline:
    def __init__(self) -> None:
        configure_logging()
        self._llm = load_text_llm()
        self._graph = build_graph(self._llm)

    def run(self, request: GenerateRequest) -> GenerateResponse:
        state = TutoringState(
            user_profile=UserProfile(
                class_level=request.class_level,
                board=request.board,
                target_exam=request.target_exam,
            ),
            image_base64=request.image_base64,
        )
        final_state = ensure_state(self._graph.invoke(state))
        return GenerateResponse(
            questions=final_state.question_bank,
            solutions=final_state.solver_output,
            evaluation=final_state.evaluation,
            diagnostics=final_state.run_diagnostics,
        )


_pipeline: Optional[Pipeline] = None


def get_pipeline() -> Pipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = Pipeline()
    return _pipeline


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "ok"}


def _validate_text_field(name: str, value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail=f"{name} is required")
    if len(cleaned) > MAX_FIELD_LENGTH:
        raise HTTPException(status_code=400, detail=f"{name} is too long")
    return cleaned


@app.post("/generate", response_model=GenerateResponse)
async def generate_questions(
    class_level: str = Form(..., alias="class"),
    board: str = Form(...),
    target_exam: str = Form(...),
    image: UploadFile = File(...),
    pipeline: Pipeline = Depends(get_pipeline),
) -> GenerateResponse:
    logger.info("Received generate request")
    try:
        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=400, detail="Unsupported image type")
        content = await image.read()
        if len(content) > MAX_IMAGE_BYTES:
            raise HTTPException(status_code=400, detail="Image too large")
        if not content:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        class_level_clean = _validate_text_field("class", class_level)
        board_clean = _validate_text_field("board", board)
        target_exam_clean = _validate_text_field("target_exam", target_exam)
        request = GenerateRequest(
            image_base64=base64.b64encode(content).decode("utf-8"),
            class_level=class_level_clean,
            board=board_clean,
            target_exam=target_exam_clean,
        )
        return pipeline.run(request)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Pipeline failed: %s", exc)
        raise HTTPException(status_code=500, detail="Pipeline execution failed")
