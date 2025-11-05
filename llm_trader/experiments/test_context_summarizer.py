from pathlib import Path
import pandas as pd
from llm_trader.intelligence.context_summarizer import ContextSummarizer


# ---------------------------------------------------------------------
# Load either 5M EURUSD
# ---------------------------------------------------------------------
def load_data() -> pd.DataFrame:
    path = Path("data/raw/eurusd_5m.csv")
    print(f"using real data: {path}")
    df = pd.read_csv(path)
    # normalize column names
    df.columns = [c.lower() for c in df.columns]
    # ensure timestamp column is parsed
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df.tail(200)  # recent 200 bars for context



# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
def main():
    df = load_data()
    summarizer = ContextSummarizer()
    summary = summarizer.summarize(df)

    print("\n=== CONTEXT SUMMARY ===")
    print(summary.text)
    print("\n=== STRUCTURED FEATURES ===")
    for k, v in summary.features.as_dict().items():
        print(f"{k:15s}: {v}")


# ---------------------------------------------------------------------
# Run in VSCode Debug
# ---------------------------------------------------------------------
if __name__ == "__main__":
    main()
