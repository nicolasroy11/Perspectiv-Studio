from pathlib import Path
import pandas as pd
from strategies.llm_trader.runner.historical_runner import HistoricalRunner

template_hist_file = "llm_trader/experiments/eurusd_5m.csv"

if __name__ == "__main__":
    runner = HistoricalRunner(
        data_path=Path(template_hist_file),
        output_dir=Path("data/backtests"),
        window_size_days=30,
        step_size_days=5,
        rsi_window=7,
        initial_balance=100000,
        risk_per_trade=0.01,
        reward_pips=1,
        risk_pips=3,
        pip_size=0.0001,
        lookahead=10,
    )


    # execute and inspect output
    metrics_df = runner.run()
    print(metrics_df)
