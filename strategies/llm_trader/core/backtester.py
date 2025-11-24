from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from dataclasses import dataclass


# ------------------------------------------------------------------ #
#   Dataclass for metrics — fully typed and testable
# ------------------------------------------------------------------ #
@dataclass(slots=True)
class BacktestMetrics:
    total_trades: int
    win_rate: float
    expectancy: float
    profit_factor: float
    sharpe_ratio: float
    equity_curve: np.ndarray
    average_win: float
    average_loss: float
    rr_ratio: float

    @property
    def as_dict(self) -> dict[str, float]:
        """Return numeric metrics as dict (excluding array)."""
        return {
            "total_trades": self.total_trades,
            "win_rate": self.win_rate,
            "expectancy": self.expectancy,
            "profit_factor": self.profit_factor,
            "sharpe_ratio": self.sharpe_ratio,
            "average_win": self.average_win,
            "average_loss": self.average_loss,
            "rr_ratio": self.rr_ratio,
        }

    def __str__(self) -> str:
        return (
            f"Trades: {self.total_trades} | WinRate: {self.win_rate*100:.1f}% | "
            f"Expectancy: {self.expectancy:.3f}R | PF: {self.profit_factor:.2f} | "
            f"Sharpe: {self.sharpe_ratio:.2f}"
        )


# ------------------------------------------------------------------ #
#   Main Backtester class (stateless functional core)
# ------------------------------------------------------------------ #
class Backtester:
    @staticmethod
    def run(
        df: pd.DataFrame,
        initial_balance: float,
        risk_per_trade: float,
        reward_pips: float,
        risk_pips: float,
        show_chart: bool = False,
    ) -> BacktestMetrics:
        """
        Run a single backtest on a labeled DataFrame.

        Args:
            df: Must include 'outcome' column (1=win, 0=loss, -1=expired).
            initial_balance: Starting capital in base currency.
            risk_per_trade: Fraction of balance risked per trade (e.g., 0.01 = 1%).
            reward_pips / risk_pips: Used for RR calculation.
            show_chart: If True, plots equity curve.

        Returns:
            BacktestMetrics
        """

        # --- Input validation ---
        if initial_balance <= 0:
            raise ValueError("initial_balance must be positive.")
        if not (0 < risk_per_trade <= 1):
            raise ValueError("risk_per_trade must be between 0 and 1.")
        if reward_pips <= 0 or risk_pips <= 0:
            raise ValueError("reward_pips and risk_pips must be positive nonzero values.")

        if "outcome" not in df.columns:
            raise ValueError("DataFrame must contain an 'outcome' column")

        # Filter valid trades (exclude NaN / expired)
        trades = df[df["outcome"].isin([0, 1])].copy()
        if trades.empty:
            return Backtester._empty_metrics()

        rr_ratio = reward_pips / risk_pips

        wins = trades[trades["outcome"] == 1]
        losses = trades[trades["outcome"] == 0]

        total_trades = len(trades)
        win_rate = len(wins) / total_trades if total_trades > 0 else 0.0
        loss_rate = 1.0 - win_rate

        # Expectancy per trade (in R)
        expectancy = (win_rate * rr_ratio) - (loss_rate * 1.0)

        # Profit factor = gross wins / gross losses
        gross_profit = len(wins) * rr_ratio
        gross_loss = len(losses)
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.inf

        # Average win/loss
        average_win = rr_ratio if len(wins) > 0 else 0.0
        average_loss = 1.0 if len(losses) > 0 else 0.0

        # Generate equity curve (in account currency)
        risk_amount = initial_balance * risk_per_trade
        trade_returns = np.where(trades["outcome"] == 1, rr_ratio, -1.0)
        equity_curve = Backtester._compute_equity_curve(trade_returns, risk_amount, initial_balance)

        # Compute Sharpe ratio (trade-level approximation)
        sharpe_ratio = Backtester._compute_sharpe(trade_returns)

        metrics = BacktestMetrics(
            total_trades=total_trades,
            win_rate=win_rate,
            expectancy=expectancy,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe_ratio,
            equity_curve=equity_curve,
            average_win=average_win,
            average_loss=average_loss,
            rr_ratio=rr_ratio,
        )

        if show_chart:
            Backtester._plot_equity(equity_curve)

        return metrics

    # ------------------------------------------------------------------ #
    @staticmethod
    def _compute_equity_curve(
        trade_returns: np.ndarray,
        risk_amount: float,
        initial_balance: float,
    ) -> np.ndarray:
        """Simulate equity progression from trade outcomes."""
        pnl = trade_returns * risk_amount
        return np.cumsum(np.insert(pnl, 0, initial_balance))

    # ------------------------------------------------------------------ #
    @staticmethod
    def _compute_sharpe(trade_returns: np.ndarray) -> float:
        """Approximate Sharpe ratio from discrete trade returns."""
        if len(trade_returns) < 2:
            return 0.0
        mean_ret = np.mean(trade_returns)
        std_ret = np.std(trade_returns, ddof=1)
        if std_ret == 0:
            return 0.0
        return float(mean_ret / std_ret * np.sqrt(len(trade_returns)))

    # ------------------------------------------------------------------ #
    @staticmethod
    def _plot_equity(equity_curve: np.ndarray) -> None:
        """Display equity curve chart."""
        plt.figure(figsize=(10, 5))
        plt.plot(equity_curve, linewidth=1.6)
        plt.title("Equity Curve")
        plt.xlabel("Trade #")
        plt.ylabel("Balance")
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

    # ------------------------------------------------------------------ #
    @staticmethod
    def _empty_metrics() -> BacktestMetrics:
        """Return zeroed metrics if no trades are present."""
        return BacktestMetrics(
            total_trades=0,
            win_rate=0.0,
            expectancy=0.0,
            profit_factor=0.0,
            sharpe_ratio=0.0,
            equity_curve=np.array([]),
            average_win=0.0,
            average_loss=0.0,
            rr_ratio=0.0,
        )
