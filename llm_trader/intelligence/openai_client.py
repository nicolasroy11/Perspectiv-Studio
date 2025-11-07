from __future__ import annotations

import time
from dataclasses import dataclass
from openai import OpenAI

import runtime_settings
from .llm_client import LLMClient


@dataclass(slots=True)
class OpenAILLM(LLMClient):
    """
    Minimal OpenAI-backed LLM client that conforms to LLMClient
    Usage:
        llm = OpenAILLM(model="gpt-4o-mini")
        text = llm("Summarize ...")
    """
    model: str
    api_key: str
    max_retries: int = 2
    timeout_s: int = 20
    temperature: float = 0.2
    verbose: bool = True

    def __post_init__(self) -> None:
        key = runtime_settings.OPENAI_API_KEY
        self._client = OpenAI(api_key=key)

    def __call__(self, prompt: str) -> str:
        """Invoke the model with a text prompt and return raw text."""
        for attempt in range(self.max_retries + 1):
            try:
                if self.verbose:
                    print("\n[OpenAILLM] >>> Sending prompt:")
                    print(prompt[:1500] + ("..." if len(prompt) > 1500 else ""))

                response = self._client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a concise trading decision assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=self.temperature,
                )

                content = response.choices[0].message.content.strip()
                if self.verbose:
                    print("\n[OpenAILLM] <<< Response:")
                    print(content)

                return content

            except Exception as e:
                print(f"[OpenAILLM] error on attempt {attempt+1}/{self.max_retries+1}: {e}")
                if attempt < self.max_retries:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                raise RuntimeError(f"OpenAILLM call failed: {e}") from e