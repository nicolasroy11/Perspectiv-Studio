# rules_based/strategies/rsi_lowrider/backtest.py

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List
import pandas as pd
import pandas_ta as ta

from brokers.tradelocker import TradeLockerBroker
from models.candle import Candle
from models.forex_instrument import ForexInstrument
from brokers.backtest import BacktestBroker
from models.position import Position
from models.trade import Trade
from strategies.rules_based.rsi_lowrider.dto.backtest_results_dto import LowriderBacktestResultsDto, LowriderCandleState
from strategies.rules_based.rsi_lowrider.strategy import RSILowriderStrategy, RSILowriderConfig
from strategies.rules_based.rsi_lowrider.logger import BacktestLogger
from web.trader_backend.schemas.backtest import BacktestRequest, RsiLowriderBacktestRequest


@dataclass
class BacktestResult:
    candles: list[Candle]
    equity_curve: list[float]
    positions: List[Position]
    trades: List[Trade]


class RSILowriderBacktester:

    def __init__(self, config: RSILowriderConfig = RSILowriderConfig()):
        self.strategy = RSILowriderStrategy(config)
        self.instrument = ForexInstrument(
                            symbol="EURUSD",
                            pip_size=0.0001,
                            dollars_per_pip_per_lot=10.0,
                            description="Euro vs US Dollar"
                        )

    # ------------------------------------------------------------
    # CSV of real TL 1m candles
    # ------------------------------------------------------------
    def load_csv(self, path: str) -> list[Candle]:
        df = pd.read_csv(path)

        candles: list[Candle] = []
        for _, row in df.iterrows():
            candles.append(
                Candle(
                    timestamp=pd.to_datetime(row["timestamp"]),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row["volume"]),
                )
            )
        return candles
    
    async def get_backtest_results(self, request: RsiLowriderBacktestRequest) -> LowriderBacktestResultsDto:
        """
        Main entry point for API-level backtesting.
        Accepts a BacktestRequest and returns the DTO used by the front-end.
        """
        
        config = RSILowriderConfig(
            rsi_period=request.rsi_period,
            rsi_oversold_level=request.rsi_oversold_level,
            rung_size_in_pips=request.rung_size_in_pips,
            tp_target_in_pips=request.tp_target_in_pips,
        )
        strategy = RSILowriderStrategy(config)

        # --------------------------
        # 2. Load candles in range
        # --------------------------
        broker = BacktestBroker()

        # candles = broker.get_candles_range_from_tradelocker(
        #     symbol=request.asset,
        #     resolution=request.frequency,
        #     date_from=request.date_from,
        #     date_to=request.date_to
        # )
        
        import os
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        CSV_PATH = os.path.join(BASE_DIR, "../../../data/raw/lowrider_1m_backtest_tradelocker_output.csv")
        candles = broker.get_candles_range_from_csv(
            file_path=CSV_PATH,
            resolution=request.frequency,
            date_from=request.date_from,
            date_to=request.date_to
            )

        series: list[LowriderCandleState] = []

        # --------------------------
        # 3. Main simulation loop
        # --------------------------
        for candle in candles:
            
            broker.process_candle(candle)
            strategy.on_candle(broker, candle)

            # Compute RSI manually for DTO
            closes = [c.close for c in strategy._candles]
            if len(closes) >= config.rsi_period + 1:
                rsi_series = ta.rsi(pd.Series(closes), length=config.rsi_period)
                rsi = float(rsi_series.iloc[-1])
            else:
                rsi = 0.0

            position = broker.get_active_position()
            active_trades = broker.get_open_trades()

            # Snapshot counts
            num_active = len([t for t in active_trades if not t.is_pending])
            num_pending = len([t for t in active_trades if t.is_pending])
            num_closed = sum(1 for p in broker.positions for t in p.trades if t.exit_price is not None)

            # Equity
            unreal = broker.unrealized_pnl(candle.close)
            real = broker.realized_pnl()
            equity = real + unreal

            # Ladder depth
            deepest = max((t.ladder_position for t in active_trades), default=0)

            # --------------------------
            # Build DTO entry
            # --------------------------
            state = LowriderCandleState(
                timestamp=str(candle.timestamp),
                open=candle.open,
                high=candle.high,
                low=candle.low,
                close=candle.close,
                volume=candle.volume,

                rsi=rsi,
                rsi_was_below_buy=strategy._last_rsi <= strategy.config.rsi_oversold_level,
                rsi_curl=(rsi > strategy._last_rsi),

                anchor_triggered=False,      # you can patch when implementing event capture
                rung_added=None,
                events=[],                   # TODO: wire events

                deepest_rung=deepest,
                active_rungs=num_active,
                pending_rungs=num_pending,

                num_active_trades=num_active,
                num_pending_trades=num_pending,
                num_closed_trades=num_closed,

                entry_prices=[t.entry_price for t in active_trades],
                tp_prices=[t.tp_price for t in active_trades if t.tp_price],

                realized_pnl=real,
                unrealized_pnl=unreal,
                equity=equity,
            )

            series.append(state)

        # Return final bundle
        return LowriderBacktestResultsDto(series=series)

    # ------------------------------------------------------------
    # MAIN BACKTEST LOOP
    # ------------------------------------------------------------
    def run_and_visualize(self, csv_path: str, plot: bool = False) -> BacktestResult:

        broker = BacktestBroker(symbol=self.instrument.symbol)
        candles = self.load_csv(csv_path)

        equity_curve = []
        all_positions = []
        all_trades = []

        for candle in candles:

            # Key: position & trade processing happens AFTER strategy logic
            # but BEFORE we compute unrealized PnL
            self.strategy.on_candle(broker, candle)
            broker.process_candle(candle)

            # Build equity: realized + unrealized
            pos = broker.get_active_position()

            if pos is None:
                equity_curve.append(0.0)
            else:
                unreal = broker.unrealized_pnl(candle.close)
                real = broker.realized_pnl()
                equity_curve.append(real + unreal)

        # snapshot finished trades
        for p in broker.positions:
            all_positions.append(p)
            for t in p.trades:
                all_trades.append(t)
                
        result = BacktestResult(
            candles=candles,
            equity_curve=equity_curve,
            positions=all_positions,
            trades=all_trades,
        )
        
        if plot:
            # ======================================================================
            # PLOT: Price with entry/exit markers + Equity curve
            # ======================================================================
            import matplotlib.pyplot as plt

            closes = [c.close for c in candles]
            times = [c.timestamp for c in candles]

            fig, ax1 = plt.subplots(figsize=(14,6))

            # --- Price line ---
            ax1.plot(times, closes, label="Close Price", linewidth=1.2)

            # --- Plot trade markers (entries & exits) ---
            for trade in all_trades:

                # ENTRY marker
                ax1.scatter(
                    trade.open_time,
                    trade.entry_price,
                    color="green",
                    marker="^",
                    s=80,
                    label="Entry" if trade == all_trades[0] else ""
                )

                # EXIT marker
                if trade.exit_price is not None:
                    ax1.scatter(
                        trade.close_time,
                        trade.exit_price,
                        color="red",
                        marker="v",
                        s=80,
                        label="Exit" if trade == all_trades[0] else ""
                    )

            ax1.set_title("Price with Entry/Exit Markers")
            ax1.set_ylabel("Price")
            ax1.grid(True)
            ax1.legend(loc="upper left")

            # --- Equity curve (right axis) ---
            ax2 = ax1.twinx()
            # ax2.plot(times, equity_curve, color="blue", linewidth=1.1, alpha=0.7, label="Equity")
            ax2.set_ylabel("Equity")
            ax2.legend(loc="upper right")
            
            # ------------------------ RSI LINE ------------------------
            # Full price series
            price_series = pd.Series(closes)

            # Compute RSI
            rsi_raw = ta.rsi(price_series, length=self.strategy.config.rsi_period)

            # Drop NaNs (warm-up period)
            valid = ~rsi_raw.isna()

            rsi_series = rsi_raw[valid]
            times_rsi = [times[i] for i in range(len(times)) if valid.iloc[i]]

            # Plot RSI
            fig_rsi, ax_rsi = plt.subplots(figsize=(14, 3))

            ax_rsi.plot(times_rsi, rsi_series, color="orange", linewidth=1.2, label="RSI")
            ax_rsi.axhline(self.strategy.config.rsi_oversold_level, color="red", linestyle="--", linewidth=1.0, label="Buy Level")

            ax_rsi.set_ylim(0, 100)
            ax_rsi.set_ylabel("RSI")
            ax_rsi.set_title("RSI Confirmation")
            ax_rsi.legend(loc="upper left")

            plt.show()

            i = 0

        return result

    def _build_candle_state(
        self,
        candle: Candle,
        broker: BacktestBroker,
        rsi: float,
        rsi_was_below_buy: bool,
        rsi_curl: bool,
        anchor_triggered: bool,
        rung_added: int | None,
        events: list[str],
    ):
        """Create a LowriderCandleState snapshot for this candle."""

        position = broker.get_active_position()
        trades = position.trades if position else []

        active_trades = [t for t in trades if t.exit_price is None and not t.is_pending]
        pending_trades = [t for t in trades if t.is_pending]
        closed_trades = [t for t in trades if t.exit_price is not None]

        realized = sum(t.realized_pnl or 0 for t in closed_trades)
        unreal = 0.0
        if position:
            last_close = candle.close
            for t in active_trades:
                unreal += (last_close - t.entry_price) * t.lot_size * 10000 * 0.1  # simplified

        equity = realized + unreal

        # deepest rung = max ladder_position among trades (even pending)
        deepest_rung = max((t.ladder_position for t in trades), default=0)

        return LowriderCandleState(
            timestamp=str(candle.timestamp),
            open=candle.open,
            high=candle.high,
            low=candle.low,
            close=candle.close,
            volume=candle.volume,

            rsi=rsi,
            rsi_was_below_buy=rsi_was_below_buy,
            rsi_curl=rsi_curl,

            anchor_triggered=anchor_triggered,
            rung_added=rung_added,
            events=events,

            deepest_rung=deepest_rung,
            active_rungs=len(active_trades),
            pending_rungs=len(pending_trades),

            num_active_trades=len(active_trades),
            num_pending_trades=len(pending_trades),
            num_closed_trades=len(closed_trades),
            entry_prices=[t.entry_price for t in active_trades],
            tp_prices=[t.tp_price for t in active_trades if t.tp_price is not None],

            realized_pnl=realized,
            unrealized_pnl=unreal,
            equity=equity,
        )

        

# csv_path = "data/raw/lowrider_1m_backtest_tradelocker_output.csv"
# backtester = RSILowriderBacktester()

# now = datetime.now()
# request = RsiLowriderBacktestRequest(
#     asset = 'EURUSD',
#     frequency = '1m',
#     dateFrom = now - timedelta(days=20),
#     dateTo = now,
#     rsi_period = 14,
#     rsi_oversold_level = 30,
#     rung_size_in_pips = 2.0,
#     tp_target_in_pips = 2.0
# )
    

# result = backtester.get_backtest_results(request=request)

# print(len(result.positions))
# print(result.equity_curve[-50:])