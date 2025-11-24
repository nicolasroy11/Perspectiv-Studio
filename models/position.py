from dataclasses import dataclass

from models.trade import Trade


@dataclass
class Position:
    symbol: str
    trades: list[Trade]

    @property
    def is_closed(self) -> bool:
        # If there are no actual fills, it's not a real position yet.
        any_filled = any(not t.is_pending for t in self.trades)
        if not any_filled:
            return False

        # A position is closed when all FILLED trades are closed
        return all(
            (t.is_pending or t.exit_price is not None)
            for t in self.trades
        )
