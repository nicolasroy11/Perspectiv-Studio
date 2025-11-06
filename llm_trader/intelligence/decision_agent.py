# llm_trader/intelligence/decision_agent.py
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Protocol

from llm_trader.intelligence.context_summarizer import (
    ContextSummary,
    FeatureSet,
)

# ---------------------------------------------------------------------
# LLM protocol (structural typing)
# Any backend that implements __call__(prompt:str)->str will work.
# ---------------------------------------------------------------------
class LLMClient(Protocol):
    def __call__(self, prompt: str) -> str: ...


# ---------------------------------------------------------------------
# Decision types & result container
# ---------------------------------------------------------------------
class Decision(Enum):
    ENTER = auto()
    SKIP = auto()
    REVERSE = auto()  # optional for future logic; safe default is SKIP

@dataclass(slots=True)
class DecisionResult:
    """
    Final, parsed decision returned by the agent.

    action:   Decision enum (ENTER | SKIP | REVERSE)
    confidence: 0.0 - 1.0 (LLM-reported self-confidence; use heuristically)
    rationale: brief natural-language reason (logged/displayed; not used in math)
    """
    action: Decision
    confidence: float
    rationale: str

    def as_dict(self) -> dict[str, str | float]:
        return {
            "action": self.action.name,
            "confidence": float(self.confidence),
            "rationale": self.rationale,
        }


# ---------------------------------------------------------------------
# DecisionAgent: composes prompt, calls LLM, parses robustly
# ---------------------------------------------------------------------
class DecisionAgent:
    """
    Turns a ContextSummary into a structured trade decision via an LLM.
    - Strict JSON output contract.
    - Robust parsing (JSON-first, regex fallback).
    - Safe defaults (SKIP on ambiguity).
    """

    def __init__(self, llm_client: LLMClient) -> None:
        self.llm = llm_client

    def evaluate(
        self,
        context: ContextSummary,
        setup_name: str,
        rr_ratio: float,
        lookahead_bars: int,
    ) -> DecisionResult:
        """
        Ask the LLM to decide if we should ENTER or SKIP the detected setup.

        Parameters
        ----------
        context : ContextSummary
            Text + features snapshot from the summarizer.
        setup_name : str
            Human label for the setup (e.g., "RSI<30_breakout").
        rr_ratio : float
            Reward:Risk ratio that the rules engine will use (e.g., 1.6 means 1.6R target, 1R stop).
        lookahead_bars : int
            How many bars we typically give the setup to resolve (information for the LLM only).

        Returns
        -------
        DecisionResult
        """
        prompt = self._build_prompt(context, setup_name, rr_ratio, lookahead_bars)
        raw = self.llm(prompt)
        return self._parse_response(raw)

    # ----------------------- internals -----------------------

    def _build_prompt(
        self,
        context: ContextSummary,
        setup_name: str,
        rr_ratio: float,
        lookahead_bars: int,
    ) -> str:
        f: FeatureSet = context.features

        # The output is strictly JSON
        return f"""You are a trading decision assistant.
                You will receive a short textual context and structured numeric features for a {setup_name} signal.
                You must respond with STRICT JSON only (no prose) in this schema:
                {{"action": "ENTER|SKIP|REVERSE", "confidence": 0.0-1.0, "reason": "brief one-liner"}}

                Guardrails:
                - Prefer SKIP when evidence is weak, contradictory, or unclear.
                - ENTER only when the probability of success is meaningfully above the base rate.
                - REVERSE is rare; use only if strong evidence indicates the opposite direction.

                Setup info:
                - Planned RR ratio: {rr_ratio:.3f}
                - Typical resolution window (bars): {lookahead_bars}

                Context (text):
                {context.text}

                Context (features):
                {json.dumps(f.as_dict(), default=str)}

                Now respond with STRICT JSON only:
                """

    def _parse_response(self, raw: str) -> DecisionResult:
        # --- 1) Try strict JSON first
        action, conf, reason = None, None, None
        try:
            data = json.loads(raw)
            action = str(data.get("action", "")).strip().upper()
            conf = float(data.get("confidence", 0.0))
            reason = str(data.get("reason", "")).strip()
        except Exception:
            # --- 2) Fallback: regex dig-out
            action = self._regex_pick(raw, r'"action"\s*:\s*"(?P<a>ENTER|SKIP|REVERSE)"', default="SKIP")
            conf_s = self._regex_pick(raw, r'"confidence"\s*:\s*(?P<c>0?\.\d+|1(?:\.0)?)', default="0.0")
            reason = self._regex_pick(raw, r'"reason"\s*:\s*"(?P<r>.*?)"', default="(no reason)")
            try:
                conf = float(conf_s)
            except Exception:
                conf = 0.0

        # --- sanitize
        action_enum = {
            "ENTER": Decision.ENTER,
            "SKIP": Decision.SKIP,
            "REVERSE": Decision.REVERSE,
        }.get(action or "SKIP", Decision.SKIP)

        conf = min(max(conf if conf is not None else 0.0, 0.0), 1.0)
        reason = reason or "(no reason)"

        return DecisionResult(action=action_enum, confidence=conf, rationale=reason)

    @staticmethod
    def _regex_pick(text: str, pattern: str, default: str) -> str:
        m = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        return (m.group(1) if m and m.lastindex else (m.groupdict().get(list(m.groupdict().keys())[0]) if m else None)) or default


# ---------------------------------------------------------------------
# Minimal mock backend for tests / dev - mihgt keep it, might not
# ---------------------------------------------------------------------
class MockLLM:
    """
    Deterministic local backend for tests/dev.
    - If RSI is oversold & trend up, ENTER.
    - If RSI overbought & trend down, REVERSE (rare).
    - Else SKIP.
    Produces valid JSON consistently.
    """
    def __call__(self, prompt: str) -> str:
        # crude but deterministic rules extracted from prompt text
        p_lower = prompt.lower()
        enter = ("rsi zone: oversold" in p_lower and "trend: up" in p_lower) or \
                ("breaks previous high" in p_lower and "ema_fast > ema_slow" in p_lower)
        reverse = ("rsi zone: overbought" in p_lower and "trend: down" in p_lower)

        if enter and not reverse:
            return json.dumps({"action": "ENTER", "confidence": 0.72, "reason": "Oversold bounce with bullish structure"})
        if reverse:
            return json.dumps({"action": "REVERSE", "confidence": 0.61, "reason": "Overbought in a downtrend; mean reversion likely"})

        return json.dumps({"action": "SKIP", "confidence": 0.35, "reason": "Signals mixed or weak"})


__all__ = [
    "DecisionAgent",
    "Decision",
    "DecisionResult",
    "LLMClient",
    "MockLLM",
]
