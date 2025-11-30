from dataclasses import dataclass
from datetime import datetime
from typing import List, Literal
from collections import defaultdict

from models.forex_instrument import ForexInstrument
from models.trade import Trade
import runtime_settings as rs


@dataclass
class Position:
    '''
    A position is the combination of one opening trade and its corresponding closing trade (or trades if partial closes are accepted)
    '''
    id: str
    status: str
    cycle_id: str
    symbol: str
    lot_size: float
    side: str
    
    open_time: datetime
    close_time: datetime

    entry_price: float
    exit_price: float
    
    nominal_tp_price: float

    gross_pnl: float
    net_pnl: float
    commission: float
    
    trades: List[Trade]

    # Lowrider-specific metadata
    position_depth: int
    
    @staticmethod
    def from_tradelocker_trades(trades: List[Trade], current_price: float, cycle_id: str, instrument: ForexInstrument) -> List['Position']:
        positions = []
        trades_by_position = defaultdict(list)
        for t in trades:
            trades_by_position[t.raw["positionId"]].append(t)
        
        for position_id, trades in trades_by_position.items():
            if position_id is None: continue
            real_trades = [trade for trade in trades if trade.status!='cancelled' and trade.status!='refused']
            real_trades.sort(key=lambda trade: trade.open_time)
            if len(real_trades) != 2:
                t = 0
            opening_trade = real_trades[0]
            closing_trade  = real_trades[-1]
            position_depth = Trade._extract_position_depth(opening_trade)
            open_time = opening_trade.open_time
            entry_price = opening_trade.executed_price
            symbol = opening_trade.symbol
            lot_size = opening_trade.lot_size
            side = opening_trade.side
            commission = round(rs.ROUNDTRIP_COMMISSION_PER_LOT * lot_size, 2)
            
            is_closed = len(real_trades) == 2 and opening_trade.side != closing_trade.side and all([t.status=='filled' for t in real_trades])
            if is_closed:
                close_time = closing_trade.open_time
                exit_price = closing_trade.executed_price
                status='closed'
                
                pip_diff = (closing_trade.executed_price - opening_trade.executed_price) / instrument.pip_size
                pip_value = instrument.dollars_per_pip_per_lot * lot_size
                gross_pnl = round(pip_diff * pip_value, 2)
                net_pnl = round(gross_pnl - commission, 2)
            else:
                close_time = None
                exit_price = current_price
                status='active'
                
                pip_diff = (current_price - opening_trade.executed_price) / instrument.pip_size
                pip_value = instrument.dollars_per_pip_per_lot * lot_size
                gross_pnl = round(pip_diff * pip_value, 2)
                net_pnl = round(gross_pnl - commission, 2)
            
            tp_price = opening_trade.tp_price
            
            positions.append(Position(
                id=position_id,
                cycle_id=cycle_id,
                symbol=symbol,
                status=status,
                side=side,
                open_time=open_time,
                close_time=close_time,
                entry_price=entry_price,
                exit_price=exit_price,
                lot_size=lot_size,
                nominal_tp_price=tp_price,
                gross_pnl=gross_pnl,
                net_pnl=net_pnl,
                commission=commission,
                trades=trades,
                position_depth=position_depth
            ))
            
        return positions
        