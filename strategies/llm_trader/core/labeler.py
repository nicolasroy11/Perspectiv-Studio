import numpy as np
import pandas as pd

def label_trades(
    df: pd.DataFrame,
    reward_pips: float,
    risk_pips: float,
    lookahead: int,
    pip_size: float = 0.0001,
) -> pd.DataFrame:
    """
    Labels only rows with `setup == True` as win(1), loss(0), or expired(-1).
    All other rows remain NaN.
    """
    df = df.copy()
    df["outcome"] = np.nan

    for i in range(len(df) - lookahead):
        # skip any row that is not a setup
        if not bool(df.iloc[i]["setup"]):
            continue

        entry = df.iloc[i]["close"]
        stop = entry - risk_pips * pip_size
        target = entry + reward_pips * pip_size

        highs = df["high"].iloc[i + 1 : i + 1 + lookahead]
        lows = df["low"].iloc[i + 1 : i + 1 + lookahead]

        hit_target_idx = highs[highs >= target].index.min()
        hit_stop_idx = lows[lows <= stop].index.min()

        # only assign outcome if this row is a setup
        if pd.isna(hit_target_idx) and pd.isna(hit_stop_idx):
            df.at[df.index[i], "outcome"] = -1  # expired
        elif pd.isna(hit_stop_idx):
            df.at[df.index[i], "outcome"] = 1
        elif pd.isna(hit_target_idx):
            df.at[df.index[i], "outcome"] = 0
        elif hit_target_idx < hit_stop_idx:
            df.at[df.index[i], "outcome"] = 1
        else:
            df.at[df.index[i], "outcome"] = 0

    # leave all non-setup rows untouched (NaN)
    return df
