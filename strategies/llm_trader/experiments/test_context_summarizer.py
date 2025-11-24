from pathlib import Path
import pandas as pd
from strategies.llm_trader.core import indicator_engine
from strategies.llm_trader.intelligence.context_summarizer import ContextSummarizer

template_hist_file = "llm_trader/experiments/eurusd_5m.csv"

def load_data() -> pd.DataFrame:
    path = Path(template_hist_file)
    if path.exists():
        print(f"using real data: {path}")
        df = pd.read_csv(path)
        df.columns = [c.lower() for c in df.columns]
        if "timestamp" in df.columns: df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.tail(500)
    else:
        raise FileNotFoundError(f"{template_hist_file} not found")

def main():
    df = load_data()
    df = indicator_engine.add_indicators(
        df,
        rsi_window = 7,
        ema_fast = 12,
        ema_slow = 26,
        adx_window = 14,
        atr_window = 14)
    
    summarizer = ContextSummarizer()
    summary = summarizer.summarize(df)

    print("\n=== CONTEXT SUMMARY ===")
    print(summary.text)

    print("\n=== STRUCTURED FEATURES ===")
    for k, v in summary.features.as_dict().items():
        print(f"{k:15s}: {v}")

if __name__ == "__main__":
    main()
