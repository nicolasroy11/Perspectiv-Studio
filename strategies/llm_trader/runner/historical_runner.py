"""
historical_runner.py
--------------------
Runs rolling-window backtests over historical data and saves performance metrics.
"""

from __future__ import annotations
from pathlib import Path
import pandas as pd
from strategies.llm_trader.core import data_loader, indicator_engine, setup_detector, labeler, backtester


class HistoricalRunner:
    """Run rolling backtests over long time spans for stability evaluation."""

    def __init__(
        self,
        data_path: str | Path,
        output_dir: str | Path,
        window_size_days: int,
        step_size_days: int,
        rsi_window: int,
        reward_pips: float,
        risk_pips: float,
        lookahead: int,
        pip_size: float,
        initial_balance: float,
        risk_per_trade: float,
    ) -> None:
        self.data_path = Path(data_path)
        self.output_dir = Path(output_dir)
        self.window_size_days = window_size_days
        self.step_size_days = step_size_days
        self.rsi_window = rsi_window
        self.reward_pips = reward_pips
        self.risk_pips = risk_pips
        self.lookahead = lookahead
        self.pip_size = pip_size
        self.initial_balance = initial_balance
        self.risk_per_trade = risk_per_trade

        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    def run(self) -> pd.DataFrame:
        """Run backtests across rolling windows and save metrics."""
        df = data_loader.load_ohlcv(self.data_path)
        if df.empty:
            print("⚠️ No data found.")
            return pd.DataFrame()

        # Add indicators and setups
        df = indicator_engine.add_rsi(df, window=self.rsi_window)
        df = setup_detector.detect_rsi_reversal_breakout(df)
        df = labeler.label_trades(
            df,
            reward_pips=self.reward_pips,
            risk_pips=self.risk_pips,
            lookahead=self.lookahead,
            pip_size=self.pip_size,
        )

        # Rolling-window backtests
        metrics_records: list[dict[str, float]] = []
        timestamps = pd.to_datetime(df["timestamp"])
        start_date = timestamps.min()
        end_date = timestamps.max()

        current_start = start_date
        while current_start < end_date:
            window_end = current_start + pd.Timedelta(days=self.window_size_days)
            window_df = df[(timestamps >= current_start) & (timestamps < window_end)]
            if len(window_df) > 10:  # skip empty/small slices
                metrics = backtester.Backtester.run(
                    df=window_df,
                    initial_balance=self.initial_balance,
                    risk_per_trade=self.risk_per_trade,
                    reward_pips=self.reward_pips,
                    risk_pips=self.risk_pips,
                )
                metrics_records.append(
                    {"start": current_start, "end": window_end, **metrics.as_dict}
                )
            current_start += pd.Timedelta(days=self.step_size_days)

        result_df = pd.DataFrame(metrics_records)
        if result_df.empty:
            print("⚠️ No metrics generated.")
            return result_df

        # Save results
        parquet_path = self.output_dir / "historical_metrics.parquet"
        json_path = self.output_dir / "historical_metrics.json"
        result_df.to_parquet(parquet_path, index=False)
        result_df.to_json(json_path, orient="records", indent=2)

        print(f"✅ Saved results: {parquet_path} and {json_path}")
        return result_df
