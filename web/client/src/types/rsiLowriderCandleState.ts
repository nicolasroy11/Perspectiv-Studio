export interface RsiLowriderCandleState {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;

  rsi: number;
  rsi_was_below_buy: boolean;
  rsi_curl: boolean;

  anchor_triggered: boolean;
  rung_added: number | null;
  events: string[];

  deepest_rung: number;
  active_rungs: number;
  pending_rungs: number;

  num_active_trades: number;
  num_pending_trades: number;
  num_closed_trades: number;

  entry_prices: number[];
  tp_prices: number[];

  realized_pnl: number;
  unrealized_pnl: number;
  equity: number;
}

export interface RsiLowriderBacktestResultsDto {
  series: RsiLowriderCandleState[];
}
