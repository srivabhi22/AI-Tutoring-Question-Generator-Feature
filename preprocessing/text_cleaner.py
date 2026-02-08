#!/usr/bin/env python3
"""
This file answers given any LLM-generated text, how do we turn it into clean, readable,
line-preserving educational content?
"""

# preprocessing/text_cleaner.py

import re
import markdown
from bs4 import BeautifulSoup
from pylatexenc.latex2text import LatexNodes2Text

# -------------------------------------------------
# Unicode maps (digits only — IMPORTANT)
# -------------------------------------------------

SUPERSCRIPT_MAP = str.maketrans({
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
    "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"
})

SUBSCRIPT_MAP = str.maketrans({
    "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄",
    "5": "₅", "6": "₆", "7": "₇", "8": "₈", "9": "₉"
})


# -------------------------------------------------
# Chemistry-safe arrow normalization
# -------------------------------------------------

def normalize_reaction_arrows(text: str) -> str:
    if not isinstance(text, str):
        return text

    # Arrow with catalyst / condition written on it
    text = re.sub(
        r"\\xrightarrow\s*\{([^}]+)\}",
        r" →[\1] ",
        text
    )

    # Equilibrium arrow
    text = re.sub(r"\\leftrightarrow", " ⇌ ", text)

    # Simple arrows
    text = re.sub(r"\\rightarrow|\\to", " → ", text)

    return text


# -------------------------------------------------
# Subscript / Superscript normalization
# -------------------------------------------------

def normalize_scripts(text: str) -> str:
    if not isinstance(text, str):
        return text

    # Subscripts: _2 or _{2}
    text = re.sub(
        r"_\{?([0-9]+)\}?",
        lambda m: m.group(1).translate(SUBSCRIPT_MAP),
        text
    )

    # Superscripts: ^2 or ^{2}
    text = re.sub(
        r"\^\{?([0-9]+)\}?",
        lambda m: m.group(1).translate(SUPERSCRIPT_MAP),
        text
    )

    return text


# -------------------------------------------------
# Markdown → plain text (structure-safe)
# -------------------------------------------------

def markdown_to_text(md_text: str) -> str:
    html = markdown.markdown(md_text, extensions=["extra"])
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator=" ")


# -------------------------------------------------
# LaTeX → plain text
# -------------------------------------------------

_LATEX_CONVERTER = LatexNodes2Text()

def latex_to_text_safe(text: str) -> str:
    if not isinstance(text, str):
        return text
    return _LATEX_CONVERTER.latex_to_text(text)


# -------------------------------------------------
# Line-preserving normalization (CORE LOGIC)
# -------------------------------------------------

def normalize_text_preserve_lines(text: str) -> str:
    """
    Cleans text while preserving line order and paragraph structure.
    - Removes Markdown / LaTeX noise
    - Preserves meaningful blank lines
    - Collapses multiple blank lines into one
    """

    if not isinstance(text, str):
        return text

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    lines = text.split("\n")
    cleaned_lines = []
    previous_blank = False

    for line in lines:
        # Remove math delimiters
        line = re.sub(r"\$(.*?)\$", r"\1", line)

        # Arrow semantics first
        line = normalize_reaction_arrows(line)

        # Markdown → text
        line = markdown_to_text(line)

        # Sub / superscripts
        line = normalize_scripts(line)

        # LaTeX → text
        line = latex_to_text_safe(line)

        # Normalize spaces inside line
        line = re.sub(r"\s+", " ", line).strip()

        if line == "":
            if not previous_blank:
                cleaned_lines.append("")
            previous_blank = True
        else:
            cleaned_lines.append(line)
            previous_blank = False

    # Remove leading/trailing blank lines
    while cleaned_lines and cleaned_lines[0] == "":
        cleaned_lines.pop(0)
    while cleaned_lines and cleaned_lines[-1] == "":
        cleaned_lines.pop()

    return "\n".join(cleaned_lines)


# -------------------------------------------------
# Public API (used everywhere)
# -------------------------------------------------

def clean_llm_string(text: str) -> str:
    return normalize_text_preserve_lines(text)


def clean_llm_json(obj):
    if isinstance(obj, dict):
        return {k: clean_llm_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_llm_json(v) for v in obj]
    elif isinstance(obj, str):
        return clean_llm_string(obj)
    else:
        return obj
