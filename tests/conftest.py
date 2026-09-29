"""Pytest defaults: never call real Claude CLI / remote LLM during unit tests."""

from __future__ import annotations

import os

# Must run before LlmClient reads env in imported modules' later calls.
os.environ.setdefault("TDT_LLM_CLI_FALLBACK", "0")
os.environ.setdefault("TDT_PIPELINE_LLM", "0")
os.environ.setdefault("TDT_ROOM_LLM", "0")
os.environ.setdefault("TDT_DEFAULT_CODING_EXECUTOR", "mock")
