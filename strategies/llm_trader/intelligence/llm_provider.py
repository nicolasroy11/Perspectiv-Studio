from __future__ import annotations
from typing import Protocol
import os
import requests
import random

import runtime_settings


# ======================================================================
# PROTOCOL
# ======================================================================
class LLMClient(Protocol):
    """Protocol for interchangeable LLM backends."""
    def __call__(self, prompt: str) -> str: ...


# ======================================================================
# MOCK CLIENT
# ======================================================================
class MockLLM:
    def __init__(self, fixed_reply: str = "SKIP — no signal."):
        self.fixed_reply = fixed_reply

    def __call__(self, prompt: str) -> str:
        # optional pseudo-random noise to simulate realism
        random.seed(42)
        return self.fixed_reply


# ======================================================================
# OLLAMA CLIENT
# ======================================================================
class OllamaLLM:
    """
    Connects to a local or dockerized Ollama instance.
    Deterministic if temperature=0 and seed fixed.
    """

    def __init__(
        self,
        model: str = "llama3",
        base_url: str = "http://localhost:11434",
        temperature: float | None = None,
        seed: int | None = None,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.temperature = temperature if temperature is not None else float(os.getenv("LLM_TEMPERATURE", "0"))
        self.seed = seed if seed is not None else int(os.getenv("LLM_SEED", "42"))

    def __call__(self, prompt: str) -> str:
        resp = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "seed": self.seed,
                },
            },
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "").strip()


# ======================================================================
# OPENAI CLIENT
# ======================================================================
class OpenAILLM:
    """
    Connects to the OpenAI API (gpt-4o-mini, gpt-4-turbo, etc.).
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float =0.2,
        seed: int = 42,
    ) -> None:
        import openai
        self.model = model
        self.temperature = temperature
        self.seed = seed
        self.client = openai.OpenAI(api_key=runtime_settings.OPENAI_API_KEY)

    def __call__(self, prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            temperature=self.temperature,
            seed=self.seed,
            messages=[
                {"role": "system", "content": "You are a trading assistant AI that decides whether to enter or skip setups."},
                {"role": "user", "content": prompt},
            ],
        )
        return completion.choices[0].message.content.strip()


# ======================================================================
# FACTORY
# ======================================================================
def get_llm_from_env() -> LLMClient:
    """
    Factory that returns the appropriate LLM client
    depending on environment variables.
    """
    backend = os.getenv("LLM_BACKEND", "mock").lower()
    model = os.getenv("LLM_MODEL", "llama3")

    if backend == "ollama":
        return OllamaLLM(model=model)
    elif backend == "openai":
        return OpenAILLM(model=model)
    else:
        return MockLLM("SKIP — no strong setup detected.")
