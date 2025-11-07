from __future__ import annotations
import pandas as pd
from pathlib import Path
from tqdm import tqdm

from llm_trader.intelligence.context_summarizer import ContextSummarizer
from llm_trader.intelligence.decision_agent import DecisionAgent
from llm_trader.core import data_loader
from llm_trader.intelligence.llm_provider import OpenAILLM

llm = OpenAILLM(model="gpt-4o-mini")
summarizer = ContextSummarizer()
agent = DecisionAgent(llm)

DATA_PATH = Path("llm_trader/experiments/eurusd_5m.csv")
OUTPUT_PATH = Path("data/eval/llm_decisions.parquet")

def run_evaluation(window_size: int = 50, step: int = 10) -> pd.DataFrame:
    df = data_loader.load_ohlcv(DATA_PATH)
    results = []

    for i in tqdm(range(window_size, len(df), step), desc="Evaluating windows"):
        window = df.iloc[i - window_size : i].copy()
        context = summarizer.summarize(window)
        decision = agent.evaluate(context, setup_name="RSI_Reversal", rr_ratio=1.8, lookahead_bars=10)

        results.append({
            "end_time": df["timestamp"].iloc[i - 1],
            "action": decision.action.name,
            "confidence": decision.confidence,
            "rationale": decision.rationale,
        })

    out_df = pd.DataFrame(results)
    out_df.to_parquet(OUTPUT_PATH, index=False)
    print(f"saved evaluation results to {OUTPUT_PATH}")
    return out_df


if __name__ == "__main__":
    df = run_evaluation()
    print(df.head(10))
