# core/llm_loader.py

import logging
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

logger = logging.getLogger(__name__)


def _get_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found in environment variables")
    return api_key



def load_text_llm():
    """
    LLM used for planner, analyzers, generator, solver, evaluator.
    """
    logger.info("Loading text LLM")
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=_get_api_key(),
    )
