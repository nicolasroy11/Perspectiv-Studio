from __future__ import annotations
import pytest

from strategies.llm_trader.intelligence.openai_client import OpenAILLM
import strategies.llm_trader.intelligence.openai_client as mod
import runtime_settings

class _DummyMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class _DummyChoice:
    def __init__(self, content: str) -> None:
        self.message = _DummyMessage(content)


class _DummyResp:
    def __init__(self, content: str) -> None:
        self.choices = [_DummyChoice(content)]


class _DummyChatCompletions:
    def __init__(self, content: str) -> None:
        self._content = content

    def create(self, *args, **kwargs) -> _DummyResp:  # 👈 accept any args/kwargs
        return _DummyResp(self._content)


class _DummyChat:
    def __init__(self, content: str, *args, **kwargs) -> None:
        self.completions = _DummyChatCompletions(content)


class _DummyOpenAI:
    def __init__(self, *args, **kwargs) -> None:
        self.chat = _DummyChat("OK")



def test_openai_adapter_returns_text(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mod, "OpenAI", _DummyOpenAI)
    client = OpenAILLM(model="gpt-4o-mini", api_key=runtime_settings.OPENAI_API_KEY, max_retries=0)
    out = client("ping")
    assert out == "OK"
