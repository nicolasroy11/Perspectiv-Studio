import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from llm_trader.core import data_loader, indicator_engine, setup_detector, labeler


def preview_rsi_setups(
    path: str | Path = "data/raw/eurusd_5m.csv",
    n: int = 5000,
    rsi_window: int = 7,
    reward_pips: float = 3.0,
    risk_pips: float = 3.0,
    lookahead: int = 5,
) -> None:
    df = data_loader.load_ohlcv(str(path))
    df = indicator_engine.add_rsi(df, window=rsi_window)
    df = setup_detector.detect_rsi_reversal_breakout(df)
    df = labeler.label_trades(df, reward_pips=reward_pips, risk_pips=risk_pips, lookahead=lookahead)
    df = df.tail(n).reset_index(drop=True)

    winners = df[df["outcome"] == 1]
    losers = df[df["outcome"] == 0]
    expired = df[df["outcome"] == -1]
    
    total_setups = len(winners) + len(losers) + len(expired)
    total_closed = len(winners) + len(losers)

    rr_ratio = reward_pips / risk_pips if risk_pips else 0.0
    p_win  = len(winners) / total_closed if total_closed > 0 else 0.0
    p_loss = len(losers)  / total_closed if total_closed > 0 else 0.0
    expectancy = (p_win * rr_ratio) - (p_loss * 1)

    weighted_win = (p_win * rr_ratio) / ((p_win * rr_ratio) + p_loss) if (p_win + p_loss) > 0 else 0.0
    
    fig_title = (
        f"RSI < 30 Breakout Setups — {reward_pips}:{risk_pips} RR<br>"
        f"🟩 Wins: {len(winners)} | 🟥 Losses: {len(losers)} | ⚪ Expired: {len(expired)}<br>"
        f"🏆 Raw Win Rate: {p_win*100:.1f}% | Weighted Win Rate: {weighted_win*100:.1f}% | "
        f"📈 Expectancy per trade: {expectancy:.3f} R"
    )

    # --- SUBPLOTS: price (row 1) + RSI (row 2) ---
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=("", "RSI (14)")
    )

    # --- PRICE PANEL ---
    fig.add_trace(
        go.Candlestick(
            x=df["timestamp"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="Price",
        ),
        row=1,
        col=1
    )

    # Add markers for trade outcomes
    fig.add_trace(
        go.Scatter(
            x=winners["timestamp"], y=winners["close"],
            mode="markers", name="Win",
            marker=dict(color="lime", size=18, symbol="triangle-up")
        ),
        row=1,
        col=1
    )
    fig.add_trace(
        go.Scatter(
            x=losers["timestamp"], y=losers["close"],
            mode="markers", name="Loss",
            marker=dict(color="red", size=18, symbol="triangle-down")
        ),
        row=1,
        col=1
    )
    fig.add_trace(
        go.Scatter(
            x=expired["timestamp"], y=expired["close"],
            mode="markers", name="Expired",
            marker=dict(color="gray", size=6, symbol="x")
        ),
        row=1,
        col=1
    )

    # --- RSI PANEL ---
    fig.add_trace(
        go.Scatter(
            x=df["timestamp"], y=df["rsi"],
            line=dict(color="purple", width=1.5),
            name="RSI (14)"
        ),
        row=2,
        col=1
    )

    # RSI threshold lines
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)

    # --- LAYOUT ---
    fig.update_layout(
        title=fig_title,
        height=900,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    # Axis titles
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)
    fig.update_xaxes(title_text="Timestamp", row=2, col=1)

    # --- DISPLAY ---
    import plotly.io as pio
    pio.renderers.default = "browser"
    fig.show()


if __name__ == "__main__":
    data_path = Path("data/raw/eurusd_5m.csv")
    if not data_path.exists():
        print("⚠️  Missing file:", data_path)
    else:
        preview_rsi_setups(str(data_path))
