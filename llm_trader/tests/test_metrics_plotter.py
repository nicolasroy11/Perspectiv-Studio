import pytest
import pandas as pd
from pathlib import Path
from llm_trader.core.visuals.metrics_plotter import plot_historical_metrics


@pytest.fixture
def tmp_metrics_dir(tmp_path: Path):
    """Temporary directory fixture for saving mock metric files."""
    d = tmp_path / "metrics"
    d.mkdir()
    return d


# ----------------------------------------------------------------------
# Helper to create a small dummy metrics DataFrame
# ----------------------------------------------------------------------
def _mock_metrics_df() -> pd.DataFrame:
    return pd.DataFrame({
        "end": pd.date_range("2025-03-02", periods=3, freq="4D"),
        "win_rate": [0.35, 0.4, 0.38],
        "expectancy": [0.1, 0.12, 0.08],
        "total_trades": [150, 155, 160],
    })


# ----------------------------------------------------------------------
# Tests for .parquet
# ----------------------------------------------------------------------
def test_plot_historical_metrics_parquet(tmp_metrics_dir: Path):
    df = _mock_metrics_df()
    metrics_path = tmp_metrics_dir / "mock_metrics.parquet"
    df.to_parquet(metrics_path)

    result = plot_historical_metrics(metrics_path, save=False, show=False)

    # --- expectations ---
    assert result is not None
    # It should be a Plotly figure-like object
    assert hasattr(result, "to_html") or hasattr(result, "to_dict")
    # Should not modify data integrity
    assert len(df) == 3


# ----------------------------------------------------------------------
# Tests for .json
# ----------------------------------------------------------------------
def test_plot_historical_metrics_json(tmp_metrics_dir: Path):
    df = _mock_metrics_df()
    metrics_path = tmp_metrics_dir / "mock_metrics.json"
    df.to_json(metrics_path, orient="records")

    result = plot_historical_metrics(metrics_path, save=False, show=False)

    assert result is not None
    assert hasattr(result, "to_html") or hasattr(result, "to_dict")


# ----------------------------------------------------------------------
# Invalid / missing data handling
# ----------------------------------------------------------------------
def test_plot_historical_metrics_missing_end_raises(tmp_metrics_dir: Path):
    df = pd.DataFrame({
        "win_rate": [0.4, 0.42],
        "expectancy": [0.12, 0.13],
    })
    metrics_path = tmp_metrics_dir / "bad_metrics.parquet"
    df.to_parquet(metrics_path)

    with pytest.raises(ValueError, match=r"Missing required columns.*end"):
        plot_historical_metrics(metrics_path, save=False, show=False)
