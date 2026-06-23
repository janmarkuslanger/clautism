"""Birthday flow: detect today's birthdays and send relation-aware wishes.

Local-only, powered by Ollama via the Stagehand workflow engine, with a
pluggable channel system (Telegram first).
"""

from birthday_flow.config import Config
from birthday_flow.flow import build_workflow, run_flow

__all__ = ["Config", "build_workflow", "run_flow"]
