"""Customer support resolution agent skeleton. Claude Architect, Week 1, Assignment 1."""

from .loop import MAX_TURNS, SYSTEM_PROMPT, Result, run_agent
from .session import Session
from .tools import TOOLS

__all__ = ["run_agent", "Session", "TOOLS", "SYSTEM_PROMPT", "MAX_TURNS", "Result"]
