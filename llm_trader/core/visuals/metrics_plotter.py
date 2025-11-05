import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path


def plot_historical_metrics(path: str | Path = "data/backtests/historical_metrics.parquet") -> None:
    """
    Visualize historical rolling backtest metrics with an equity curve overlay.

    Args:
        path: Path to the parquet file produced by HistoricalRunner.
    """
    df = pd.read_parquet(path)

    # --- Compute equity curve from expectancy (proxy cumulative R) ---
    df["cumulative_expectancy"] = df["expectancy"].cumsum()

    # --- Setup subplots ---
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.7, 0.3],
        subplot_titles=("Performance Metrics", "Cumulative Expectancy (Equity Curve)")
    )

    # --- Metrics traces (win rate, expectancy, sharpe) ---
    fig.add_trace(go.Scatter(
        x=df["end"], y=df["win_rate"],
        mode="lines+markers", name="Win Rate",
        line=dict(color="lime", width=2)
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df["end"], y=df["expectancy"],
        mode="lines+markers", name="Expectancy (R/trade)",
        line=dict(color="blue", width=2)
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df["end"], y=df["sharpe_ratio"],
        mode="lines+markers", name="Sharpe Ratio",
        line=dict(color="purple", width=2)
    ), row=1, col=1)

    # --- Equity curve subplot ---
    fig.add_trace(go.Scatter(
        x=df["end"], y=df["cumulative_expectancy"],
        mode="lines", name="Cumulative Expectancy",
        line=dict(color="orange", width=3)
    ), row=2, col=1)

    # --- Layout ---
    fig.update_layout(
        title="Rolling Backtest Metrics + Equity Curve",
        height=900,
        template="plotly_white",
        hovermode="x unified",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig.update_yaxes(title_text="Metric Value", row=1, col=1)
    fig.update_yaxes(title_text="Cumulative R", row=2, col=1)
    fig.update_xaxes(title_text="End Date", row=2, col=1)

    import plotly.io as pio
    pio.renderers.default = "browser"
    fig.show()


if __name__ == "__main__":
    # direct debug-run support in VSCode
    data_path = Path("data/backtests/historical_metrics.parquet")
    if data_path.exists():
        plot_historical_metrics(data_path)
    else:
        print(f"missing file: {data_path}")
