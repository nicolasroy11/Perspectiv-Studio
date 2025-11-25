export interface RsiLowriderCandleState {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;

  current_rsi_value: number;

  events: string[];

  num_active_rungs: number;
  num_pending_rungs: number;

  num_active_trades: number;
  num_pending_trades: number;
  num_closed_trades: number;

  realized_pnl: number;
  unrealized_pnl: number;
  equity: number;
}

export interface RsiLowriderBacktestResultsDto {
  series: RsiLowriderCandleState[];
}
