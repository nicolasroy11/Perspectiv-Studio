from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Dict
import numpy as np
import pandas as pd
import numpy.typing as npt


# ======================================================================
# ENUMS
# ======================================================================

class TrendState(Enum):
    UP = auto()
    DOWN = auto()
    FLAT = auto()


class RsiZone(Enum):
    OVERSOLD = auto()
    NEUTRAL = auto()
    OVERBOUGHT = auto()
    UNKNOWN = auto()


# ======================================================================
# DATA STRUCTURES
# ======================================================================

@dataclass(slots=True)
class FeatureSet:
    """Typed, serializable collection of numeric and categorical features."""
    close: float
    high: float
    low: float
    open: float
    volume: float

    rsi: Optional[float]
    ema_fast: Optional[float]
    ema_slow: Optional[float]
    adx: Optional[float]
    atr: Optional[float]

    trend_state: TrendState
    rsi_zone: RsiZone
    last_n_green: int
    last_n_red: int
    atr_rank_pct: Optional[float]

    def as_dict(self) -> Dict[str, float | int | str | None]:
        return {
            "close": self.close,
            "high": self.high,
            "low": self.low,
            "open": self.open,
            "volume": self.volume,
            "rsi": self.rsi,
            "ema_fast": self.ema_fast,
            "ema_slow": self.ema_slow,
            "adx": self.adx,
            "atr": self.atr,
            "trend_state": self.trend_state.name,
            "rsi_zone": self.rsi_zone.name,
            "last_n_green": self.last_n_green,
            "last_n_red": self.last_n_red,
            "atr_rank_pct": self.atr_rank_pct,
        }


@dataclass(slots=True)
class ContextSummary:
    """Encapsulates textual + structured feature context for the LLM."""
    text: str
    features: FeatureSet

    def __str__(self) -> str:
        return f"ContextSummary({self.features.trend_state.name}, RSI={self.features.rsi_zone.name})"


# ======================================================================
# SUMMARIZER CLASS
# ======================================================================

class ContextSummarizer:
    """
    Encapsulated class for generating LLM-ready summaries
    of recent market context (price + indicator snapshot).
    """

    def __init__(
        self,
        rsi_oversold: float = 30.0,
        rsi_overbought: float = 70.0,
        n_candles: int = 50,
        n_recent: int = 5
    ) -> None:
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.n_candles = n_candles
        self.n_recent = n_recent

    # ------------------------------------------------------------------
    def summarize(self, df: pd.DataFrame) -> ContextSummary:
        if len(df) == 0:
            raise ValueError("Empty DataFrame passed to summarizer")

        window = df.tail(self.n_candles).reset_index(drop=True)

        # --- Last bar OHLCV
        close = float(window["close"].iloc[-1])
        high = float(window["high"].iloc[-1])
        low = float(window["low"].iloc[-1])
        open_ = float(window["open"].iloc[-1])
        volume_series = window.get("volume", pd.Series([0]))
        volume = float(volume_series.iloc[-1])

        rsi = self._safe_get(window, "rsi")
        ema_fast = self._safe_get(window, "ema_fast")
        ema_slow = self._safe_get(window, "ema_slow")
        adx = self._safe_get(window, "adx")
        atr = self._safe_get(window, "atr")

        trend_state = self._trend_state(window, ema_fast, ema_slow)
        rsi_zone = self._rsi_zone(rsi)
        last_n_green, last_n_red = self._color_counts(window)
        atr_rank_pct = self._atr_rank(window, atr)

        features = FeatureSet(
            close=close, high=high, low=low, open=open_, volume=volume,
            rsi=rsi, ema_fast=ema_fast, ema_slow=ema_slow, adx=adx, atr=atr,
            trend_state=trend_state, rsi_zone=rsi_zone,
            last_n_green=last_n_green, last_n_red=last_n_red,
            atr_rank_pct=atr_rank_pct,
        )

        text = self._compose_text(window, features)
        return ContextSummary(text=text, features=features)

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------
    def _safe_get(self, df: pd.DataFrame, col: str) -> Optional[float]:
        return float(df[col].iloc[-1]) if col in df.columns and not pd.isna(df[col].iloc[-1]) else None

    def _trend_state(self, df: pd.DataFrame, ema_fast: Optional[float], ema_slow: Optional[float]) -> TrendState:
        if ema_fast is not None and ema_slow is not None:
            if ema_fast > ema_slow:
                return TrendState.UP
            elif ema_fast < ema_slow:
                return TrendState.DOWN
            return TrendState.FLAT

        x: npt.NDArray[np.float64] = np.arange(len(df), dtype=float)
        y: npt.NDArray[np.float64] = df["close"].to_numpy(dtype=float)
        slope = float(np.polyfit(x, y, 1)[0])
        return TrendState.UP if slope > 0 else TrendState.DOWN if slope < 0 else TrendState.FLAT

    def _rsi_zone(self, rsi: Optional[float]) -> RsiZone:
        if rsi is None:
            return RsiZone.UNKNOWN
        if rsi < self.rsi_oversold:
            return RsiZone.OVERSOLD
        if rsi > self.rsi_overbought:
            return RsiZone.OVERBOUGHT
        return RsiZone.NEUTRAL

    def _color_counts(self, df: pd.DataFrame) -> tuple[int, int]:
        colors = np.where(df["close"] >= df["open"], 1, -1)
        last = colors[-self.n_recent:] if len(colors) >= self.n_recent else colors
        return int((last == 1).sum()), int((last == -1).sum())

    def _atr_rank(self, df: pd.DataFrame, atr: Optional[float]) -> Optional[float]:
        if atr is None or "atr" not in df.columns:
            return None
        valid_atr_arr = np.asarray(df["atr"].dropna(), dtype=float)
        if valid_atr_arr.size == 0:
            return None
        atr_val: float = float(atr)
        return float(np.mean(valid_atr_arr <= atr_val))

    def _compose_text(self, df: pd.DataFrame, f: FeatureSet) -> str:
        parts: list[str] = [
            f"Trend: {f.trend_state.name.lower()}.",
            f"Last O/H/L/C={f.open:.5f}/{f.high:.5f}/{f.low:.5f}/{f.close:.5f}.",
            f"RSI zone: {f.rsi_zone.name.lower()}.",
            f"Recent candles: green={f.last_n_green}, red={f.last_n_red}."
        ]
        if f.ema_fast and f.ema_slow:
            cmp = ">" if f.ema_fast > f.ema_slow else "<" if f.ema_fast < f.ema_slow else "="
            parts.append(f"EMA_fast {cmp} EMA_slow.")
        if f.atr and f.atr_rank_pct:
            parts.append(f"ATR={f.atr:.6f} (rank≈{f.atr_rank_pct*100:.0f}%).")

        # breakout check
        if len(df) >= 2:
            prev_high, prev_low = float(df["high"].iloc[-2]), float(df["low"].iloc[-2])
            broke_up = f.high > prev_high
            broke_down = f.low < prev_low
            if broke_up and not broke_down:
                parts.append("Current bar breaks previous high.")
            elif broke_down and not broke_up:
                parts.append("Current bar breaks previous low.")

        return " ".join(parts)
