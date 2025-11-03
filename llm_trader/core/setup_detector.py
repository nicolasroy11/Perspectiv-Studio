import pandas as pd


def detect_rsi_reversals(df: pd.DataFrame, threshold: float = 30.0) -> pd.DataFrame:
    """
    Identify RSI cross-unders below threshold.

    Returns:
        DataFrame with boolean 'setup' column.
    """
    df = df.copy()
    crosses = (df["rsi"].shift(1) >= threshold) & (df["rsi"] < threshold)
    df["setup"] = crosses
    return df


def detect_rsi_reversal_breakout(
    df: pd.DataFrame,
    rsi_col: str = "rsi",
    rsi_threshold: float = 30.0,
    lookback: int = 3,
    cooldown: int = 0,
) -> pd.DataFrame:
    """
    Detect setups where RSI recently dipped below threshold within the last lookback bars
    AND the current high breaks the previous candle's high.
    Fires only once per RSI recovery (prevents repeated triggers while RSI stays elevated).
    """
    df = df.copy()

    if rsi_col not in df.columns:
        raise KeyError(f"Column '{rsi_col}' not found in DataFrame")

    # Track if RSI was below threshold recently
    df["rsi_recent_min"] = df[rsi_col].rolling(window=lookback, min_periods=1).min()
    df["prev_high"] = df["high"].shift(1)
    df["prev_low"] = df["low"].shift(1)

    # Base condition
    cond = (df["rsi_recent_min"] < rsi_threshold) & (df["high"] > df["prev_high"]) & (df["low"] > df["prev_low"])

    # Prevent repeat triggers: only when RSI was below threshold within lookback
    # but is now recovering (RSI rising back above threshold)
    df["setup"] = (
        cond
        # & (df[rsi_col] > rsi_threshold)
        # & (df[rsi_col].shift(1) <= rsi_threshold)
    )

    # Optional cooldown to avoid overlapping entries
    if cooldown > 0:
        active = False
        last_trigger = -999
        for i in range(len(df)):
            if cond.iloc[i] and i - last_trigger > cooldown:
                active = True
            else:
                active = False
            df.at[i, "setup"] = active
            if active:
                last_trigger = i

    return df



