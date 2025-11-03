import pandas as pd
import ta


# ---------- Individual indicator methods ---------- #

def add_rsi(df: pd.DataFrame, window: int) -> pd.DataFrame:
    """Add RSI indicator."""
    out = df.copy()
    out["rsi"] = ta.momentum.RSIIndicator(out["close"], window=window).rsi()
    return out


def add_ema(df: pd.DataFrame, fast: int, slow: int) -> pd.DataFrame:
    """Add fast and slow EMAs."""
    out = df.copy()
    out["ema_fast"] = ta.trend.EMAIndicator(out["close"], window=fast).ema_indicator()
    out["ema_slow"] = ta.trend.EMAIndicator(out["close"], window=slow).ema_indicator()
    return out


def add_adx(df: pd.DataFrame, window: int) -> pd.DataFrame:
    """Add ADX (trend strength) indicator."""
    out = df.copy()
    out["adx"] = ta.trend.ADXIndicator(out["high"], out["low"], out["close"], window=window).adx()
    return out


def add_atr(df: pd.DataFrame, window: int) -> pd.DataFrame:
    """Add ATR (volatility) indicator."""
    out = df.copy()
    out["atr"] = ta.volatility.AverageTrueRange(high=out["high"], low=out["low"], close=out["close"], window=window).average_true_range()
    return out


# ---------- Composite helper ---------- #

def add_indicators(df: pd.DataFrame, rsi_window: int, ema_fast: int, ema_slow: int, adx_window: int, atr_window: int) -> pd.DataFrame:
    """
    Compose all key indicators (RSI, EMA, ADX, ATR) into one DataFrame.

    Args:
        df: price DataFrame with ['open','high','low','close','volume'].

    Returns:
        DataFrame with added indicator columns.
    """
    out = df.copy()
    out = add_rsi(out, window=rsi_window)
    out = add_ema(out, fast=ema_fast, slow=ema_slow)
    out = add_adx(out, window=adx_window)
    out = add_atr(out, window=atr_window)
    return out.dropna().reset_index(drop=True)
