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
from models.cycle import Cycle
from models.trade import Trade
from strategies.rules_based.rsi_lowrider.dto.backtest_results_dto import LowriderBacktestResultsDto, LowriderCandleState
from strategies.rules_based.rsi_lowrider.market_signals import RSILowriderSignals
from strategies.rules_based.rsi_lowrider.logger import BacktestLogger
from web.trader_backend.schemas.backtest import BacktestRequest, RsiLowriderBacktestRequest


@dataclass
class BacktestResult:
    candles: list[Candle]
    equity_curve: list[float]
    positions: List[Cycle]
    trades: List[Trade]
    
@dataclass
class PositionEvents:
    ANCHOR = 'ANCHOR'
    TP_HIT = 'TP_HIT'
    RUNG_ADDED = 'RUNG_ADDED'
    RUNG_FILLED = 'RUNG_FILLED'
    POSITION_CLOSED = 'POSITION_CLOSED'


class RSILowriderBacktester:

    def __init__(self):
        self.strategy = RSILowriderSignals()
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

        strategy = RSILowriderSignals()
        broker = BacktestBroker()

        # -------------------------
        # 2. Load candles
        # -------------------------
        import os
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        CSV_PATH = os.path.join(
            BASE_DIR,
            "../../../data/raw/lowrider_1m_backtest_tradelocker_output.csv"
        )

        candles = broker.get_candles_range_from_csv(
            file_path=CSV_PATH,
            resolution=request.frequency,
            date_from=request.date_from,
            date_to=request.date_to
        )

        series: list[LowriderCandleState] = []

        # ------------------------------------------------------------
        # EVENT TRACKING SUPPORT
        # ------------------------------------------------------------

        def detect_anchor(previous_position_state, current_position_state) -> bool:
            """Position went from None → active (first trade is anchor). In other words, a position was just opened."""
            return previous_position_state is None and current_position_state is not None

        def detect_tp_hit(previous_num_closed_trades, current_num_closed_trades) -> bool: 
            """Closed-trade count increased → TP triggered."""
            if current_num_closed_trades > previous_num_closed_trades:
                t = 0
            return current_num_closed_trades > previous_num_closed_trades

        # For detecting rung creation and fills:
        def count_pending_rungs(position: Cycle):
            if not position:
                return 0
            return sum(1 for t in position.positions if t.is_pending)

        def count_active_rungs(position: Cycle):
            if not position:
                return 0
            return sum(1 for t in position.positions if not t.is_pending and t.exit_price is None)

        # Track previous state for event comparisons
        previous_position = None
        previous_num_closed_trades = 0
        previous_pending_rungs = 0

        # ============================================================
        # 3. MAIN LOOP
        # ============================================================
        for candle in candles:

            # Order: STRATEGY FIRST, then BROKER processing
            strategy.on_candle_just_closed(broker, candle)
            broker.process_candle(candle)

            # -------------------------
            # Compute RSI for DTO
            # -------------------------
            rsi_value = strategy.rsi_list[-1] if strategy.rsi_list else 0.0

            # -------------------------
            # Current broker state
            # -------------------------
            current_position = broker.get_active_cycle()
            active_trades = broker.get_open_trades()

            num_active_trades = len([t for t in active_trades if not t.is_pending])
            num_pending_trades = len([t for t in active_trades if t.is_pending])
            current_num_closed_trades = sum(
                1 for p in broker.positions for t in p.positions if t.exit_price is not None
            )

            # Rungs
            num_active_rungs = count_active_rungs(current_position)
            num_pending_rungs = count_pending_rungs(current_position)

            # PnL & Equity
            unrealized_pnl = broker.unrealized_pnl(candle.close)
            realized_pnl = broker.realized_pnl()
            equity = realized_pnl + unrealized_pnl

            # -------------------------
            # EVENT DETECTION
            # -------------------------
            events: list[str] = []

            # Detect anchor
            if detect_anchor(previous_position, current_position):
                events.append(PositionEvents.ANCHOR)

            # Detect TP hit
            if detect_tp_hit(previous_num_closed_trades, current_num_closed_trades):
                events.append(PositionEvents.TP_HIT)

            # Detect rung creation (increase in pending trades)
            if current_position and num_pending_rungs > previous_pending_rungs:
                events.append(PositionEvents.RUNG_ADDED)

            # Detect rung filled (pending reduced because one filled)
            if current_position and num_pending_rungs < previous_pending_rungs:
                events.append(PositionEvents.RUNG_FILLED)

            # Detect full close
            if previous_position is not None and current_position is None:
                events.append(PositionEvents.POSITION_CLOSED)

            # -------------------------
            # Store the candle state
            # -------------------------
            state = LowriderCandleState(
                timestamp=str(candle.timestamp),
                open=candle.open,
                high=candle.high,
                low=candle.low,
                close=candle.close,
                volume=candle.volume,

                current_rsi_value=rsi_value,
                events=events,

                num_active_rungs=num_active_rungs,
                num_pending_rungs=num_pending_rungs,

                num_active_trades=num_active_trades,
                num_pending_trades=num_pending_trades,
                num_closed_trades=current_num_closed_trades,

                realized_pnl=realized_pnl,
                unrealized_pnl=unrealized_pnl,
                equity=equity,
            )

            series.append(state)

            # -------------------------
            # Update previous snapshot
            # -------------------------
            previous_position = current_position
            previous_num_closed_trades = current_num_closed_trades
            previous_pending_rungs = num_pending_rungs

        # Wrap result
        dto = LowriderBacktestResultsDto(series=series)

        # Save if needed
        self.save_backtest_results_to_json(dto)

        return dto

    # ------------------------------------------------------------
    # MAIN BACKTEST LOOP
    # ------------------------------------------------------------
    def run_and_visualize(self, csv_path: str, plot: bool = False) -> BacktestResult:

        broker = BacktestBroker(symbol=self.instrument.symbol)
        candles = self.load_csv(csv_path)

        equity_curve: List[float] = []
        all_positions: List[Cycle] = []
        all_trades: List[Trade] = []

        for candle in candles:

            # Key: position & trade processing happens AFTER strategy logic
            # but BEFORE we compute unrealized PnL
            self.strategy.on_candle_just_closed(broker, candle)
            broker.process_candle(candle)

            # Build equity: realized + unrealized
            pos = broker.get_active_cycle()

            if pos is None:
                equity_curve.append(0.0)
            else:
                unreal = broker.unrealized_pnl(candle.close)
                real = broker.realized_pnl()
                equity_curve.append(real + unreal)

        # snapshot finished trades
        for p in broker.positions:
            all_positions.append(p)
            for t in p.positions:
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
                    trade.executed_price,
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

    # def _build_candle_state(
    #     self,
    #     candle: Candle,
    #     broker: BacktestBroker,
    #     rsi: float,
    #     rsi_was_below_buy: bool,
    #     rsi_curl: bool,
    #     anchor_triggered: bool,
    #     rung_added: int | None,
    #     events: list[str],
    # ):
    #     """Create a LowriderCandleState snapshot for this candle."""

    #     position = broker.get_active_position()
    #     trades = position.trades if position else []

    #     active_trades = [t for t in trades if t.exit_price is None and not t.is_pending]
    #     pending_trades = [t for t in trades if t.is_pending]
    #     closed_trades = [t for t in trades if t.exit_price is not None]

    #     realized = sum(t.realized_pnl or 0 for t in closed_trades)
    #     unreal = 0.0
    #     if position:
    #         last_close = candle.close
    #         for t in active_trades:
    #             unreal += (last_close - t.entry_price) * t.lot_size * 10000 * 0.1  # simplified

    #     equity = realized + unreal

    #     # deepest rung = max ladder_position among trades (even pending)
    #     deepest_rung = max((t.ladder_position for t in trades), default=0)

    #     return LowriderCandleState(
    #         timestamp=str(candle.timestamp),
    #         open=candle.open,
    #         high=candle.high,
    #         low=candle.low,
    #         close=candle.close,
    #         volume=candle.volume,

    #         rsi=rsi,
    #         is_last_rsi_below_buy_threshold=rsi_was_below_buy,
    #         is_current_rsi_above_last=rsi_curl,

    #         anchor_triggered=anchor_triggered,
    #         rung_added=rung_added,
    #         events=events,

    #         deepest_rung=deepest_rung,
    #         num_active_rungs=len(active_trades),
    #         num_pending_rungs=len(pending_trades),

    #         num_active_trades=len(active_trades),
    #         num_pending_trades=len(pending_trades),
    #         num_closed_trades=len(closed_trades),
    #         entry_prices=[t.entry_price for t in active_trades],
    #         tp_prices=[t.tp_price for t in active_trades if t.tp_price is not None],

    #         realized_pnl=realized,
    #         unrealized_pnl=unreal,
    #         equity=equity,
    #     )
        
    def _json_safe(self, value: LowriderBacktestResultsDto):
        """
        Convert datetimes, pandas timestamps, dataclasses, and lists
        into JSON-serializable structures.
        """
        from dataclasses import asdict, is_dataclass
        from datetime import datetime
        import pandas as pd
        from typing import Any
        # datetime → ISO string
        if isinstance(value, (datetime, pd.Timestamp)):
            return value.isoformat()

        # dataclass → dict
        if is_dataclass(value):
            return {k: self._json_safe(v) for k, v in asdict(value).items()}

        # list → list of safe values
        if isinstance(value, list):
            return [self._json_safe(v) for v in value]

        # everything else returned as-is
        return value


    def save_backtest_results_to_json(self, dto):
        """
        Serialize a LowriderBacktestResultsDto to a JSON file safely.
        Converts timestamps and nested dataclasses properly.
        """
        import os
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        CSV_PATH = os.path.join(BASE_DIR, "../../../data/raw/lowrider_backtest_output.json")
        import json
        safe_dict = self._json_safe(dto)

        with open(CSV_PATH, "w") as f:
            json.dump(safe_dict, f, indent=2)

        return CSV_PATH

        

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