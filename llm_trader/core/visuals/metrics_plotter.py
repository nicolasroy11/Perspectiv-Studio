from __future__ import annotations

import pandas as pd
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio


def plot_historical_metrics(
    metrics_path: str | Path = "data/backtests/historical_metrics.parquet",
    save: bool = True,
    show: bool = True,
) -> Path | None:
    """
    Plot rolling backtest performance trends (win rate, expectancy, sharpe ratio)

    Args:
        metrics_path: Path to metrics .parquet or .json file.
        save: If True, saves chart to PNG in same directory.
        show: If True, opens the interactive Plotly chart.

    Returns:
        Path to saved PNG chart (if saved), otherwise None.
    """
    metrics_path = Path(metrics_path)
    if not metrics_path.exists():
        raise FileNotFoundError(f"Metrics file not found: {metrics_path}")

    # --- LOAD DATA ---
    if metrics_path.suffix == ".parquet":
        df = pd.read_parquet(metrics_path)
    elif metrics_path.suffix == ".json":
        df = pd.read_json(metrics_path)
    else:
        raise ValueError("Unsupported file format (must be .parquet or .json).")

    if "end" not in df.columns:
        raise ValueError("Metrics file missing 'end' column for timeline plotting.")

    df["end"] = pd.to_datetime(df["end"])
    df = df.sort_values("end").reset_index(drop=True)

    # --- SUBPLOTS ---
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=("Win Rate", "Expectancy (R)", "Sharpe Ratio"),
        row_heights=[0.33, 0.33, 0.34],
    )

    # --- PLOTS ---
    fig.add_trace(
        go.Scatter(
            x=df["end"], y=df["win_rate"],
            mode="lines+markers",
            name="Win Rate",
            line=dict(color="royalblue", width=2),
            marker=dict(size=6),
        ),
        row=1, col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df["end"], y=df["expectancy"],
            mode="lines+markers",
            name="Expectancy (R)",
            line=dict(color="orange", width=2),
            marker=dict(size=6),
        ),
        row=2, col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df["end"], y=df["sharpe_ratio"],
            mode="lines+markers",
            name="Sharpe Ratio",
            line=dict(color="green", width=2),
            marker=dict(size=6),
        ),
        row=3, col=1,
    )

    # --- LAYOUT ---
    fig.update_layout(
        title=(
            "Historical Backtest Metrics<br>"
            "Rolling window performance trends"
        ),
        height=900,
        template="plotly_white",
        showlegend=False,
        hovermode="x unified",
        margin=dict(t=80, b=60, l=60, r=20),
    )

    fig.update_xaxes(title_text="End Date", row=3, col=1)
    fig.update_yaxes(title_text="Win Rate", row=1, col=1, tickformat=".0%")
    fig.update_yaxes(title_text="Expectancy (R)", row=2, col=1)
    fig.update_yaxes(title_text="Sharpe", row=3, col=1)

    # --- DISPLAY ---
    output_path = None
    if save:
        out_dir = metrics_path.parent / "plots"
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / "historical_metrics_plot.png"
        fig.write_image(str(output_path), scale=2)
        print(f"saved chart: {output_path}")

    if show:
        pio.renderers.default = "browser"
        fig.show()

    return output_path

if __name__ == "__main__":
    print("running metrics_plotter in debug mode...")

    default_path = Path("data/backtests/historical_metrics.parquet")
    if not default_path.exists():
        print(f"file not found: {default_path.resolve()}")
    else:
        print(f"loading metrics from: {default_path.resolve()}")
        output = plot_historical_metrics(default_path)
        if output:
            print(f"plot saved at: {output.resolve()}")
        else:
            print("chart displayed but not saved.")