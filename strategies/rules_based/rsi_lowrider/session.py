import asyncio
from datetime import datetime, timedelta, timezone
from typing import List

from brokers.base import BaseBroker
from models.account_snapshot import AccountSnapshot
from models.candle import Candle
from models.cycle import Cycle
import session_config as config
from strategies.rules_based.rsi_lowrider.strategy import RSILowriderStrategy
import session_config as config

rsi_lowrider_config = config.RSI_LOWRIDER_CONFIG

class Session:
    
    def __init__(self, broker: BaseBroker) -> None:
        self.last_seen_timestamp: datetime = None
        self.current_cycle_start: datetime = datetime.now(timezone.utc)
        self.broker = broker
        self.strategy = RSILowriderStrategy()
        
    
    async def run(self) -> None:
        """
        Outer loop = Session loop (runs forever)
        Inside it, we run a Cycle loop.
        """
        while True:
            await self.run_cycle()


    async def run_cycle(self) -> None:
        """
        Run a single trading cycle.

        A cycle begins when this method is called and ends when `loop()` returns True.
        After the cycle ends, this function returns back to Session.run(),
        which will immediately start a new cycle on the next boundary.
        """

        # Mark the start of THIS cycle
        self.current_cycle_start: datetime = datetime.now(timezone.utc)
        self.current_cycle_id = f"RSILR_{str(self.current_cycle_start)[:19]}"
        print(f"\n=== New Cycle started at {self.current_cycle_start} ===")

        loop_num = 0
        cycle_finished: bool = False
        while not cycle_finished:
            print(f"\n=== Loop {loop_num} ===")
            loop_num += 1
            cycle_finished = await self.loop()
            if cycle_finished: break

            # Wait for the next opening candle
            sleep_sec: float = self.seconds_until_next_boundary(config.INTERVAL_MINUTES)
            await asyncio.sleep(sleep_sec)


    async def loop(self) -> bool:
        """
        One iteration of the session loop:
        1. Fetch snapshot (positions, PnL, depths)
        2. Detect cycle status (terminated → new cycle)
        3. Fetch latest closed candles
        4. Detect whether candle is new
        5. Apply spread gate
        6. Evaluate strategy signal
        7. Patch all missing depths (including depth 0)
        8. Log state
        """

        # -------------------------------------------------
        # 1. SNAPSHOT
        # -------------------------------------------------
        now: datetime = datetime.now(timezone.utc)
        snapshot: AccountSnapshot = self.broker.get_account_snapshot(
            date_from=self.current_cycle_start,
            date_to=now
        )

        # -------------------------------------------------
        # 2. Detect cycle termination
        # -------------------------------------------------
        cycle_positions_exist = len(snapshot.positions) > 0
        has_open_positions = any(p.status == "active" for p in snapshot.positions)

        if cycle_positions_exist and not has_open_positions:
            print(f"[{now}] Cycle TERMINATED. Closing all orders...")

            # Close all TL positions + cancel all pending orders
            cycle_closed = await self.broker.close_all()

            # Exit this loop iteration and let parent loop restart cleanly
            return cycle_closed

        # Depth state derived from snapshot
        existing_depths: set[int] = {p.position_depth for p in snapshot.positions}
        cycle_touched: bool = len(existing_depths) > 0

        # -------------------------------------------------
        # 3. Fetch candles
        # -------------------------------------------------
        date_from_candles: datetime = now - timedelta(minutes=config.FETCH_COUNT)

        candles: List[Candle] = self.broker.get_candles_range(
            symbol=config.INSTRUMENT.symbol,
            resolution=config.CANDLES_RESOLUTION,
            date_from=date_from_candles,
            date_to=now,
        )

        if not candles:
            print("No candles returned; will try again on next boundary.")
            return False

        latest_candle: Candle = candles[-1]

        # -------------------------------------------------
        # 4. Only process NEW candles
        # -------------------------------------------------
        if self.last_seen_timestamp is not None and latest_candle.timestamp == self.last_seen_timestamp:
            print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] No new closed candle.")
            return False

        self.last_seen_timestamp = latest_candle.timestamp

        # -------------------------------------------------
        # 5. Spread gate
        # -------------------------------------------------
        spread: float = self.broker.get_current_spread()
        if spread > config.MAX_SPREAD_PIPS:
            self.log_state(latest_candle, snapshot)
            return False

        # -------------------------------------------------
        # 6. Strategy signal (pure: no broker inside)
        # -------------------------------------------------
        should_go_long: bool = self.strategy.should_enter_long_position(candles)

        # -------------------------------------------------
        # 7. Ladder patching logic
        # -------------------------------------------------
        max_depth: int = config.MAX_ALLOWABLE_SIMULTANEOUS_POSITIONS
        expected_depths: set[int] = set(range(max_depth))
        missing_depths: set[int] = expected_depths - existing_depths

        anchor_price: float = latest_candle.close
        pip: float = self.broker.instrument.pip_size

        # Only patch if:
        #   - RSI says start ladder (should_go_long) OR
        #   - ladder already started (cycle_touched)
        if should_go_long or cycle_touched:
            for depth in sorted(missing_depths):
                entry: float = anchor_price - depth * config.RSI_LOWRIDER_CONFIG.RUNG_SIZE_IN_PIPS * pip
                tp: float = entry + config.RSI_LOWRIDER_CONFIG.TP_TARGET_IN_PIPS * pip

                bid, _ = self.broker.get_current_bid_ask()
                if bid < entry:
                    continue

                self.broker.place_limit_buy(
                    entry_price=entry,
                    lot_size=config.RSI_LOWRIDER_CONFIG.LOT_SIZE,
                    tp_price=tp,
                    strategy_id=f"{self.current_cycle_id}_{depth}",
                )

        # -------------------------------------------------
        # 8. Logging
        # -------------------------------------------------
        self.log_state(latest_candle, snapshot)
        return False


    def seconds_until_next_boundary(self, interval_minutes: int) -> float:
        """Seconds until the next time where minute % interval == 0 and second == 0."""
        now = datetime.now(timezone.utc)
        # Next "rounded down" minute
        base = now.replace(second=0, microsecond=0)

        # Start from the next minute
        candidate = base + timedelta(minutes=1)

        # Find the next minute where minute % interval == 0
        while candidate.minute % interval_minutes != 0:
            candidate += timedelta(minutes=1)

        return (candidate - now).total_seconds()


    def log_state(self, latest_candle: Candle, snapshot: AccountSnapshot):
        
        now = datetime.now(timezone.utc)
        cycle_start_date = now - timedelta(days=1)  # TODO: set an actual date
        
        print("────────────────────────────────────────────────────────")
        print(f"open_gross_pnl:      {snapshot.cycle_gross_pnl:.5f}")
        print(f"open_net_pnl:        {snapshot.cycle_net_pnl:.5f}")
        print(f"[CANDLE CLOSED] {latest_candle.timestamp}")
        print("Price:")
        print(f"  close:      {latest_candle.close:.5f}")
        print(f"  spread:     {self.broker.get_current_spread():.2f} pips")

        # RSI
        prev_rsi = self.strategy.rsi_list[-2] if len(self.strategy.rsi_list) >= 2 else None
        curr_rsi = self.strategy.rsi_list[-1] if self.strategy.rsi_list else None

        print()
        print("RSI:")
        print(f"  previous:   {prev_rsi:.2f}" if prev_rsi is not None else "  previous:   n/a")
        print(f"  current:    {curr_rsi:.2f}" if curr_rsi is not None else "  current:    n/a")
        print()

        positions = snapshot.positions
        if positions: deepest = max(p.position_depth for p in positions)
        print("Cycle:")
        print(f"  ACTIVE with {len(positions)} positions")
        if positions: print(f"  deepest position: {deepest}")


        print("────────────────────────────────────────────────────────")


async def main(broker: BaseBroker) -> None:
    print(
        f"Starting RSILowrider Session "
        f"(closed candles only, every {config.INTERVAL_MINUTES} min on the minute)..."
    )

    session: Session = Session(broker=broker)
    await session.run()


if __name__ == "__main__":
    from brokers.tradelocker import TradeLockerBroker
    asyncio.run(main(TradeLockerBroker()))
    
