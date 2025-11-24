from __future__ import annotations
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.io as pio


def plot_historical_metrics(
    path: str | Path,
    save: bool = True,
    show: bool = True,
):
    """
    Load a historical backtest metrics file (.parquet or .json),
    produce an interactive plotly line chart of win_rate and expectancy over time.
    """
    path = Path(path)

    # ----------------------------------------------------------------------
    # Format detection
    # ----------------------------------------------------------------------
    if not path.exists():
        raise FileNotFoundError(f"Metrics file not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".parquet":
        df = pd.read_parquet(path)
    elif suffix == ".json":
        df = pd.read_json(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    # ----------------------------------------------------------------------
    # Validate schema
    # ----------------------------------------------------------------------
    required_cols = {"end", "win_rate", "expectancy"}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(f"Missing required columns: {missing}")

    # ----------------------------------------------------------------------
    # Plotting
    # ----------------------------------------------------------------------
    fig = px.line(
        df,
        x="end",
        y=["win_rate", "expectancy"],
        title="Historical Backtest Metrics Over Time",
        markers=True,
        labels={"value": "Metric Value", "end": "Period End", "variable": "Metric"},
    )

    fig.update_layout(
        height=600,
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    # ----------------------------------------------------------------------
    # Save / Show
    # ----------------------------------------------------------------------
    if save:
        out_path = Path("data/backtests/metrics_chart.html")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(out_path)
        print(f"✅ Saved metrics chart to {out_path}")

    if show:
        pio.renderers.default = "browser"
        fig.show()

    return fig
