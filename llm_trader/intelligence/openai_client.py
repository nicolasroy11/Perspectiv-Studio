from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Optional
from openai import OpenAI, APIStatusError, APIConnectionError, RateLimitError

import runtime_settings
from .llm_client import LLMClient


@dataclass(slots=True)
class OpenAILLM(LLMClient):
    """
    Minimal OpenAI-backed LLM client that conforms to LLMClient.
    Usage:
        llm = OpenAILLM(model="gpt-4o-mini")
        text = llm("Summarize ...")
    """
    model: str
    api_key: str
    max_retries: int = 2
    timeout_s: int = 20

    def __post_init__(self) -> None:
        key = runtime_settings.OPENAI_API_KEY
        self._client = OpenAI(api_key=key)

    def __call__(self, prompt: str) -> str:
        last_err: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a concise, deterministic trading assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.0,
                    timeout=self.timeout_s,
                )
                msg = resp.choices[0].message.content or ""
                return msg.strip()

            except (APIConnectionError, RateLimitError, APIStatusError) as e:
                last_err = e
                time.sleep(min(1.5 * (attempt + 1), 4.0))

            except Exception as e:
                raise RuntimeError(f"OpenAILLM call failed: {e}") from e

        raise RuntimeError(f"OpenAILLM exhausted retries: {last_err}")
