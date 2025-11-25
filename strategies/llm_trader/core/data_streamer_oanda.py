"""
data_streamer_oanda.py
Usage:
    export OANDA_API_KEY="your_api_token"
    export OANDA_ACCOUNT_ID="your_account_id"
    python -m llm_trader.core.data_streamer_oanda --backfill
    python -m llm_trader.core.data_streamer_oanda --stream
"""

import os
import time
import pandas as pd
import requests
from datetime import datetime, timedelta, timezone
from pathlib import Path
import argparse
import runtime_settings as rt

# ---------------- CONFIG ----------------
SYMBOL = "EUR_USD"
GRANULARITY = "M5"
DATA_PATH = Path("data/raw/eurusd_5m.csv")
OANDA_API_KEY = rt.OANDA_API_KEY
OANDA_ACCOUNT_ID = rt.OANDA_ACCOUNT_ID
OANDA_REST_URL = f"https://api-fxpractice.oanda.com/v3/instruments/{SYMBOL}/candles"
OANDA_STREAM_URL = f"https://stream-fxpractice.oanda.com/v3/accounts/{OANDA_ACCOUNT_ID}/pricing/stream"
# ----------------------------------------


def _headers():
    if not OANDA_API_KEY:
        raise RuntimeError("missing OANDA_API_KEY environment variable")
    return {"Authorization": f"Bearer {OANDA_API_KEY}"}


# ---------- HISTORICAL BACKFILL ----------
def fetch_history(start=None, end=None):
    """
    Fetch historical candles from OANDA between start and end datetimes.
    Automatically paginates if more than 5000 bars are needed.
    Example:
        fetch_history(datetime(2025,3,1, tzinfo=timezone.utc))
    """
    from datetime import datetime, timedelta, timezone

    print(f"fetching {SYMBOL} {GRANULARITY} data from OANDA...")

    if start is None:
        # default: pull last 30 days
        start = datetime.now(timezone.utc) - timedelta(days=250)
    if end is None:
        end = datetime.now(timezone.utc)

    BASE_URL = f"https://api-fxpractice.oanda.com/v3/instruments/{SYMBOL}/candles"
    step = timedelta(days=17)  # 17 days ≈ 5000 M5 candles
    current = start
    all_rows = []

    while current < end:
        next_end = min(current + step, end)
        params = {
            "from": current.isoformat(),
            "to": next_end.isoformat(),
            "granularity": GRANULARITY,
            "price": "M",
        }
        try:
            r = requests.get(BASE_URL, headers=_headers(), params=params, timeout=20)
            r.raise_for_status()
            candles = r.json().get("candles", [])
            if not candles:
                print(f"no data returned for {current.date()} -> {next_end.date()}")
            else:
                rows = [
                    {
                        "timestamp": pd.to_datetime(c["time"], utc=True),
                        "open": float(c["mid"]["o"]),
                        "high": float(c["mid"]["h"]),
                        "low": float(c["mid"]["l"]),
                        "close": float(c["mid"]["c"]),
                        "volume": c["volume"],
                    }
                    for c in candles
                    if c["complete"]
                ]
                all_rows.extend(rows)
                print(f"{len(rows):>5} bars {current.date()} → {next_end.date()}")
        except Exception as e:
            print(f"error {current.date()} → {next_end.date()}: {e}")

        current = next_end
        time.sleep(0.25)  # tiny delay to avoid rate-limit

    if not all_rows:
        raise RuntimeError("no data retrieved.")

    df = pd.DataFrame(all_rows).sort_values("timestamp")
    print(f"Total bars retrieved: {len(df)}")
    return df


# ---------- FORWARD STREAMING ----------
def append_latest(df_existing):
    """Fetch most recent candle and append if new."""
    params = {"count": 2, "granularity": GRANULARITY, "price": "M"}
    r = requests.get(OANDA_REST_URL, headers=_headers(), params=params, timeout=10)
    c = r.json()["candles"][-1]
    latest_ts = pd.to_datetime(c["time"], utc=True)

    last_saved = pd.to_datetime(df_existing["timestamp"].iloc[-1], utc=True)
    if latest_ts > last_saved:
        row = pd.DataFrame([{
            "timestamp": latest_ts,
            "open": float(c["mid"]["o"]),
            "high": float(c["mid"]["h"]),
            "low": float(c["mid"]["l"]),
            "close": float(c["mid"]["c"]),
            "volume": c["volume"]
        }])
        df = pd.concat([df_existing, row], ignore_index=True)
        print(f"added new bar @ {latest_ts}")
        return df
    else:
        print("no new bar yet.")
        return df_existing


def run_stream(interval_sec=10):
    """Poll for new 5-minute candles."""
    print("OANDA streaming mode active (checks every 10 s). Press Ctrl+C to stop.")
    df = pd.read_csv(DATA_PATH)
    while True:
        df = append_latest(df)
        df.to_csv(DATA_PATH, index=False)
        time.sleep(interval_sec)


# ---------- MAIN CLI ----------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backfill", action="store_true", help="Fetch historical data")
    parser.add_argument("--stream", action="store_true", help="Stream new candles")
    args = parser.parse_args()

    Path("data/raw").mkdir(parents=True, exist_ok=True)

    if args.backfill:
        df = fetch_history()
        df.to_csv(DATA_PATH, index=False)
        print(f"saved to {DATA_PATH}!")

    if args.stream:
        run_stream()


if __name__ == "__main__":
    main()
