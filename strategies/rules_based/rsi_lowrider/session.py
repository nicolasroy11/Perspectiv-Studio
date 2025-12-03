import asyncio
from datetime import datetime, timedelta, timezone
import time
from typing import List
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
import winsound

from brokers.base import BaseBroker
from models.account_snapshot import AccountSnapshot
from models.candle import Candle
import session_config as config
from strategies.rules_based.rsi_lowrider.market_signals import RSILowriderSignals
import session_config as config
from utils.logging import print_and_log_info, print_and_log_milestone, print_and_log_warning

rsi_lowrider_config = config.RSI_LOWRIDER_CONFIG

class Session:
    
    def __init__(self, broker: BaseBroker, createPhysicalLogs: bool=False) -> None:
        self.last_seen_timestamp: datetime = None
        self.broker = broker
        self.signals = RSILowriderSignals()
        self.createPhysicalLogs = createPhysicalLogs
        self.log_file_path = ''
        
    
    async def run(self) -> None:
        """
        Outer loop = Session loop (runs forever)
        Inside it, we run a Cycle loop.
        """
        
        print_and_log_milestone(
            f"Starting RSILowrider Session "
            f"(closed candles only, every {config.INTERVAL_MINUTES} min on the minute)...",
            self.log_file_path
        )
        # sleep_sec: float = self.seconds_until_next_boundary(config.INTERVAL_MINUTES)
        # await asyncio.sleep(sleep_sec)
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
        self.broker.refresh()
        self.current_cycle_start: datetime = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(seconds=2)
        safe_timestamp = self.current_cycle_start.strftime("%Y-%m-%d_%H-%M-%S")
        self.current_cycle_id = f"RSILR_{safe_timestamp[:19]}"
        if self.createPhysicalLogs: self.log_file_path = f"{BASE_DIR}/logs/{safe_timestamp}.txt"
        
        print_and_log_milestone(f"\n=== New Cycle started at {self.current_cycle_start} ===", self.log_file_path)
        
        now: datetime = datetime.now(timezone.utc)
        self.initial_snapshot: AccountSnapshot = self.broker.get_account_snapshot(
            date_from=self.current_cycle_start,
            date_to=now
        )
        self.initial_balance = self.initial_snapshot.account_balance

        loop_num = 0
        cycle_finished: bool = False
        while not cycle_finished:
            print_and_log_milestone(f"\n------------------------- Loop {loop_num} ------------------------- ", self.log_file_path)
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
        actions_taken = []
        # -------------------------------------------------
        # 1. INITIAL SNAPSHOT
        # -------------------------------------------------
        now: datetime = datetime.now(timezone.utc)
        initial_snapshot: AccountSnapshot = self.broker.get_account_snapshot(
            date_from=self.current_cycle_start,
            date_to=now
        )

        # -------------------------------------------------
        # 2. Detect cycle termination
        # -------------------------------------------------
        cycle_positions_exist = len(initial_snapshot.activated_positions) > 0
        has_open_positions = any(p.status == "active" for p in initial_snapshot.activated_positions)

        if cycle_positions_exist and not has_open_positions:
            self.log_state(Candle.empty(), initial_snapshot, [])
            print_and_log_milestone(f"[{now}] Cycle TERMINATED. Closing all orders...", self.log_file_path)
            print_and_log_milestone(f"Final Cycle PnL: {self.initial_balance - initial_snapshot.account_balance}", self.log_file_path)

            # Close all TL positions + cancel all pending orders
            cycle_closed = await self.broker.close_all()

            # Exit this loop iteration and let parent loop restart cleanly
            return cycle_closed

        # Depth state derived from snapshot
        existing_depths: set[int] = {p.position_depth for p in initial_snapshot.activated_positions}
        cycle_touched: bool = len(existing_depths) > 0

        # -------------------------------------------------
        # 3. Fetch candles
        # -------------------------------------------------
        date_from_candles: datetime = now - timedelta(minutes=config.FETCH_COUNT)
        
        candles = self.get_candles(date_from=date_from_candles, date_to=now)

        if not candles:
            print_and_log_warning("No candles returned; will try again on next boundary.", self.log_file_path)
            return False

        latest_candle: Candle = candles[-1]

        # -------------------------------------------------
        # 4. Only process NEW candles
        # -------------------------------------------------
        if self.last_seen_timestamp is not None and latest_candle.timestamp == self.last_seen_timestamp:
            print_and_log_warning(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] No new closed candle. Trying again...", self.log_file_path)
            time.sleep(2)
            candles = self.get_candles(date_from=date_from_candles, date_to=now)
            latest_candle: Candle = candles[-1]

        self.last_seen_timestamp = latest_candle.timestamp

        # -------------------------------------------------
        # 5. Spread gate
        # -------------------------------------------------
        spread: float = self.broker.get_current_spread()
        spread_is_acceptable = spread <= config.MAX_SPREAD_PIPS
        
        # -------------------------------------------------
        # 6. Strategy signal (pure: no broker inside)
        # -------------------------------------------------
        should_go_long: bool = self.signals.should_enter_long_position(candles)
        if should_go_long:
            print_and_log_milestone(f"should_go_long: {should_go_long}", self.log_file_path)
            
            winsound.Beep(500, 1000)  # frequency=1000Hz, duration=1000ms

        # -------------------------------------------------
        # 7. Ladder patching logic
        # -------------------------------------------------
        max_depth: int = config.MAX_ALLOWABLE_SIMULTANEOUS_POSITIONS
        expected_depths: set[int] = set(range(max_depth))
        missing_depths: set[int] = expected_depths - existing_depths

        anchor_price: float = latest_candle.close
        pip: float = self.broker.instrument.pip_size

        # Only patch if RSI says start ladder (should_go_long) OR ladder already started (cycle_touched)
        if (should_go_long or cycle_touched) and spread_is_acceptable:
            if missing_depths:
                print_and_log_milestone(f"missing_depths: {missing_depths}", self.log_file_path)
                for depth in sorted(missing_depths):
                    entry_price: float = anchor_price - depth * config.RSI_LOWRIDER_CONFIG.POSITION_DISTANCE_IN_PIPS * pip
                    tp: float = entry_price + config.RSI_LOWRIDER_CONFIG.TP_TARGET_IN_PIPS * pip

                    bid, _ = self.broker.get_current_bid_ask()
                    if bid < entry_price:
                        continue

                    self.broker.place_limit_buy(
                        entry_price=entry_price,
                        lot_size=config.RSI_LOWRIDER_CONFIG.LOT_SIZE,
                        tp_price=tp,
                        strategy_id=f"{self.current_cycle_id}_{depth}",
                    )
                    winsound.Beep(1000, 1000)  # frequency=1000Hz, duration=500ms
                    
                    actions_taken.append(f"Limit buy {config.RSI_LOWRIDER_CONFIG.LOT_SIZE} lots at {entry_price} with TP {tp}")

        # -------------------------------------------------
        # 1. FINAL SNAPSHOT
        # -------------------------------------------------
        now: datetime = datetime.now(timezone.utc)
        final_snapshot: AccountSnapshot = self.broker.get_account_snapshot(
            date_from=self.current_cycle_start,
            date_to=now
        )
        
        # -------------------------------------------------
        # 8. Logging
        # -------------------------------------------------
        self.log_state(latest_candle, final_snapshot, actions_taken)
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
    
    
    def get_candles(self, date_from, date_to):
        candles: List[Candle] = self.broker.get_candles_range(
            symbol=config.INSTRUMENT.symbol,
            resolution=config.CANDLES_RESOLUTION,
            date_from=date_from,
            date_to=date_to,
        )
        return candles


    def log_state(self, latest_candle: Candle, snapshot: AccountSnapshot, actions_taken: List[str]=[]):
        positions = snapshot.activated_positions
        print_and_log_info(f"[CANDLE CLOSED] {latest_candle.timestamp}", self.log_file_path)
        print()
        
        print_and_log_info(f"acct_open_gross_pnl:      {snapshot.account_open_gross_pnl:.2f}", self.log_file_path)
        print_and_log_info(f"acct_open_net_pnl:        {snapshot.account_open_net_pnl:.2f}", self.log_file_path)
        print_and_log_info(f"cycle_open_gross_pnl:     {snapshot.cycle_open_gross_pnl:.2f}", self.log_file_path)
        print_and_log_info(f"cycle_open_net_pnl:       {snapshot.cycle_open_net_pnl:.2f}", self.log_file_path)
        print_and_log_info(f"cycle_net_realized_pnl:   {sum([p.net_pnl for p in positions if p.status=='closed']):.2f}", self.log_file_path)
        print()
        
        print_and_log_info("Price:", self.log_file_path)
        print_and_log_info(f"  close:      {latest_candle.close:.5f}", self.log_file_path)
        print_and_log_info(f"  spread:     {self.broker.get_current_spread():.2f} pips", self.log_file_path)
        print()
        
        # RSI
        prev_rsi = self.signals.rsi_list[-2] if len(self.signals.rsi_list) >= 2 else None
        curr_rsi = self.signals.rsi_list[-1] if self.signals.rsi_list else None
        print_and_log_info("RSI:", self.log_file_path)
        print_and_log_info(f"  previous:   {prev_rsi:.2f}" if prev_rsi is not None else "  previous:   n/a", self.log_file_path)
        print_and_log_info(f"  current:    {curr_rsi:.2f}" if curr_rsi is not None else "  current:    n/a", self.log_file_path)
        print()
        
        print_and_log_milestone(f"Actions taken: {actions_taken}", self.log_file_path)
        print()

        
        if positions: deepest = max(p.position_depth for p in positions)
        print_and_log_info("Cycle:", self.log_file_path)
        print_and_log_info(f"  Pending positions:   {snapshot.num_pending_positions}", self.log_file_path)
        print_and_log_info(f"  Activated positions: {len(positions)}", self.log_file_path)
        if positions:
            for p in positions:
                print_and_log_info(str(p), self.log_file_path)


async def main(broker: BaseBroker) -> None:
    session: Session = Session(broker=broker, createPhysicalLogs=True)
    await session.run()


if __name__ == "__main__":
    from brokers.tradelocker import TradeLockerBroker
    asyncio.run(main(TradeLockerBroker()))
    
