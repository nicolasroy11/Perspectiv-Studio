# llm_trader/intelligence/llm_client.py
from __future__ import annotations
from typing import Protocol

class LLMClient(Protocol):
    """
    Common interface for all LLM backends.
    Each backend (mock, OpenAI, Ollama, etc.)
    must implement __call__(prompt) -> str
    returning a raw JSON/text reply.
    """
    def __call__(self, prompt: str) -> str: ...
