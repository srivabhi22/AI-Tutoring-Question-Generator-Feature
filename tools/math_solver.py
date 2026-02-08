#!/usr/bin/env python3

from langchain.tools import tool

@tool
def python_math(code: str) -> str:
    """
    Execute Python code for mathematical computation.
    Only use for calculations.
    """
    try:
        local_env = {}
        exec(code, {}, local_env)
        return str(local_env)
    except Exception as e:
        return f"Error: {e}"