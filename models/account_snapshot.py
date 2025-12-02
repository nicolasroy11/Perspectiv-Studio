
from dataclasses import dataclass
from typing import List

from models.position import Position


@dataclass
class AccountSnapshot:
    cycle_gross_pnl: float
    cycle_net_pnl: float
    account_open_gross_pnl: float
    account_open_net_pnl: float
    account_balance: float
    account_projected_balance: float
    account_cash_balance: float
    unsettled_cash: float
    activated_positions: List[Position]
    num_pending_positions: int
    