from __future__ import annotations
from asyncio import sleep
from dataclasses import dataclass

import requests
from datetime import datetime, timedelta, timezone
import time
from typing import Any, List, Optional, Tuple

from models.account_snapshot import AccountSnapshot
from models.forex_instrument import ForexInstrument
from data.constants.forex_instruments import ForexInstruments
from models.position import Position
import runtime_settings as rs
from models.candle import Candle
from models.trade import Trade
from brokers.base import BaseBroker

@dataclass
class TLInstrument(ForexInstrument):
    tradable_id: int = 0
    info_route_id: int = 0
    trade_route_id: int = 0
    
class APIMappings:
    account_status: List[str]
    orders_history_mappings: List[str]
    orders_mappings: List[str]
    filled_orders_mappings: List[str]
    

class TradeLockerBroker(BaseBroker):
    """
    Unified TradeLocker interface.
    This single class handles:
      - Authentication
      - Account and instrument lookup
      - Candle history
      - Market and limit order placement
      - Adding rungs (limit buy with corresponding TP)
      - Flattening cycles
      - Mapping TL API -> internal models (Candle, Trade, Cycle)

    This replaces the old TradeLockerClient and the old Broker wrapper entirely.
    """

    def __init__(
        self,
        email: str = rs.TRADELOCKER_EMAIL,
        password: str = rs.TRADELOCKER_PASSWORD,
        server: str = rs.TRADELOCKER_SERVER,
        base_url: str = rs.TRADELOCKER_BASE_API_URL,
        instrument_name: str = 'EURUSD',
        account_id: Optional[str] = None,
    ):
        self.email = email
        self.password = password
        self.server = server
        self.base_url = base_url

        self.token: Optional[str] = None
        self.account_id = account_id
        
        if not self.ping():
            print('SERVER NOT AVAILABLE')
        else:
            print('server available')
        
        
        self.authenticate()
        if self.account_id is None:
            self.auto_assign_account()
            
        self.set_instrument_parameters(instrument_name)
        
        
    def refresh(self):
        
        self.set_api_mappings()


    # ----------------------------------------------------------------------
    # Authentication
    # ----------------------------------------------------------------------
    def authenticate(self):
        url = f"{self.base_url}/auth/jwt/token"
        payload = {
            "email": self.email,
            "password": self.password,
            "server": self.server,
        }
        headers = {"accept": "application/json", "content-type": "application/json"}

        r = requests.post(url, json=payload, headers=headers)
        if r.status_code != 201:
            raise RuntimeError(f"TradeLocker auth failed: {r.text}")

        data = r.json()
        self.token = data["accessToken"]

    def get_auth_headers(self):
        if not self.token:
            raise RuntimeError("Not authenticated")
        return {
            "accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "accNum": "2",
        }
        
    def ping(self) -> bool:
        ping = requests.get(f"{self.base_url}/ping")
        accessible = ping.status_code == 200
        return accessible

    # ----------------------------------------------------------------------
    # Account / instrument discovery
    # ----------------------------------------------------------------------
    def auto_assign_account(self):
        url = f"{self.base_url}/auth/jwt/all-accounts"
        r = requests.get(url, headers=self.get_auth_headers())

        if r.status_code != 200:
            raise RuntimeError(f"Could not fetch accounts: {r.text}")

        accounts = r.json()["accounts"]
        if not accounts:
            raise RuntimeError("No TL accounts available")

        self.account_id = accounts[0]["id"]

    def set_instrument_parameters(self, instrument_name: str):
        url = f"{self.base_url}/trade/accounts/{self.account_id}/instruments"
        r = requests.get(url, headers=self.get_auth_headers())
        if r.status_code != 200:
            raise RuntimeError(f"Could not fetch instruments: {r.text}")

        instruments = r.json()
        selected_instrument = [item for item in instruments['d']['instruments'] if item["name"]==instrument_name][0]
        
        _info_route = [route for route in selected_instrument['routes'] if route["type"]=='INFO'][0]
        _trade_route = [route for route in selected_instrument['routes'] if route["type"]=='TRADE'][0]
        init: ForexInstrument = getattr(ForexInstruments, instrument_name)
        self.instrument = TLInstrument(
            symbol = instrument_name,
            pip_size = init.pip_size,
            dollars_per_pip_per_lot = init.dollars_per_pip_per_lot,
            info_route_id = _info_route['id'],
            trade_route_id = _trade_route['id'],
            tradable_id = selected_instrument['tradableInstrumentId']
        )
        
        
    def set_api_mappings(self):
        mappings = APIMappings()
        url: str = f"{self.base_url}/trade/config"
        headers: dict = self.get_auth_headers()
        r = requests.get(url, headers=headers)
        config_data: dict = r.json()
        mappings.orders_mappings = [field['id'] for field in config_data['d']['ordersConfig']['columns']]
        mappings.filled_orders_mappings = [field['id'] for field in config_data['d']['filledOrdersConfig']['columns']]
        mappings.orders_history_mappings = [field['id'] for field in config_data['d']['ordersHistoryConfig']['columns']]
        mappings.account_status = [field['id'] for field in config_data['d']['accountDetailsConfig']['columns']]
        self.api_mappings = mappings


    # ----------------------------------------------------------------------
    # Candle Retrieval
    # ----------------------------------------------------------------------
    def get_candles(
        self,
        symbol: str,
        resolution: str,
        minutes: int,
    ) -> List[Candle]:
        """
        Convenience: get last N minutes of candles.
        """
        now = datetime.now(timezone.utc)
        return self.get_candles_range(
            symbol=symbol,
            resolution=resolution,
            date_from=now - timedelta(minutes=minutes),
            date_to=now,
        )

    def get_candles_range(
        self,
        symbol: str,
        resolution: str,
        date_from: datetime,
        date_to: datetime,
    ) -> List[Candle]:
        """
        Main candle retrieval method.
        """

        if date_from.tzinfo is None:
            date_from = date_from.replace(tzinfo=timezone.utc)
        if date_to.tzinfo is None:
            date_to = date_to.replace(tzinfo=timezone.utc)

        from_ms = int(date_from.timestamp() * 1000)
        to_ms = int(date_to.timestamp() * 1000)

        url = f"{self.base_url}/trade/history"
        params = {
            "routeId": self.instrument.info_route_id,
            "from": from_ms,
            "to": to_ms,
            "resolution": resolution,
            "tradableInstrumentId": self.instrument.tradable_id,
        }

        r = requests.get(url, headers=self.get_auth_headers(), params=params)
        if r.status_code != 200:
            raise RuntimeError(f"Failed to fetch candles: {r.text}")

        return self._convert_bars_to_candles(r.json())

    def _convert_bars_to_candles(self, data: dict) -> List[Candle]:
        bars = []
        if "barDetails" in data:
            bars = data["barDetails"]
        elif "d" in data and "barDetails" in data["d"]:
            bars = data["d"]["barDetails"]
        else:
            print(f"Invalid TL candle schema: {data}")

        out: List[Candle] = []
        if not bars:
            print(f"no bars: {data}")
        for bar in bars:
            ts = datetime.fromtimestamp(bar["t"] / 1000, tz=timezone.utc)
            out.append(
                Candle(
                    timestamp=ts,
                    open=bar["o"],
                    high=bar["h"],
                    low=bar["l"],
                    close=bar["c"],
                    volume=bar.get("v", 0),
                )
            )
        return out
    
    def get_current_bid_ask(self) -> Tuple[float, float]:
        """
        Fetch the current bid/ask for the instrument using TL's quotes endpoint.
        Response schema:
        {
        "d": {
            "bp": <bid>,
            "bs": <size>,
            "ap": <ask>,
            "as": <size>
        },
        "s": "ok"
        }
        """

        url: str = f"{self.base_url}/trade/quotes"

        params = {
            "routeId": "452",                      # same routeId as candles
            "tradableInstrumentId": self.instrument.tradable_id,
        }

        headers = self.get_auth_headers()

        r = requests.get(url, headers=headers, params=params)
        if r.status_code != 200:
            raise RuntimeError(f"Failed to fetch quotes: {r.text}")

        data = r.json()

        # Validate schema
        if "d" not in data or "bp" not in data["d"] or "ap" not in data["d"]:
            raise RuntimeError(f"Unexpected quote schema: {data}")

        bid: float = float(data["d"]["bp"])
        ask: float = float(data["d"]["ap"])

        return (bid, ask)
    
    def get_current_spread(self) -> float:
        bid, ask = self.get_current_bid_ask()
        spread_in_pips = (ask - bid) / self.instrument.pip_size
        return spread_in_pips


    # ----------------------------------------------------------------------
    # Order Placement
    # ----------------------------------------------------------------------
    
    def place_limit_buy(
        self,
        entry_price: float,
        lot_size: float,
        tp_price: float | None = None,
        strategy_id: str | None = None,
    ) -> str:
        """
        Create a LIMIT BUY order with optional take-profit.
        """

        url: str = f"{self.base_url}/trade/accounts/{self.account_id}/orders"

        # --- Required params for LIMIT BUY ---
        payload: dict = {
            "routeId": self.instrument.trade_route_id,
            "tradableInstrumentId": self.instrument.tradable_id,
            "type": "limit",                      # LIMIT order
            "side": "buy",                        # BUY
            "price": entry_price,                 # LIMIT price
            "qty": lot_size,                      # units, *not* lots? (TL uses units)
            "validity": "GTC"
        }

        # --- Strategy tag for algorithmic trading ---
        if strategy_id:
            payload["strategyId"] = strategy_id[:31]   # limit enforced by API

        # --- Optional Take Profit ---
        if tp_price is not None:
            payload["takeProfit"] = tp_price
            payload["takeProfitType"] = "absolute"     # we always use absolute TP

        # --- Headers ---
        headers: dict = self.get_auth_headers()
        
        # --- prevent buying at a loss ---
        bid, _ = self.get_current_bid_ask()
        if bid < entry_price: return ''     # if the immediate price has already gone below our entry_price, we do not buy, return a falsy value

        # --- HTTP Request ---
        r = requests.post(url, json=payload, headers=headers)

        if r.status_code != 200:
            raise RuntimeError(
                f"Failed to place LIMIT BUY: {r.text}\nPayload sent: {payload}"
            )

        data: dict = r.json()

        if "d" not in data or "orderId" not in data["d"]:
            raise RuntimeError(f"TraderLocker error: {data}")

        order_id: str = data["d"]["orderId"]
        return order_id


    def add_rung(
        self,
        entry_price: float,
        lot_size: float,
        tp_price: float | None = None,
        strategy_id: str | None = None,
        ladder_position: int | None = None
    ) -> str:
        """
        Add a rung = limit buy + fixed TP 2 pips above.
        Limit order enters → TP placed immediately.
        """
        order_id = self.place_limit_buy(
            lot_size=lot_size,
            entry_price=entry_price,
            tp_price=tp_price,
            strategy_id=strategy_id
        )
        return order_id


    # ----------------------------------------------------------------------
    # Cycle Control
    # ----------------------------------------------------------------------
    def close_cycle_market(self, cycle_id: str) -> None:
        """
        Flatten at market.
        """
        # TODO implement TL endpoint
        raise NotImplementedError("Implement TL close cycle endpoint")
    
    
    def get_account_snapshot(self, date_from: datetime, date_to: datetime) -> AccountSnapshot:
        """
        Fetch most recent cycle state.
        """
        
        headers: dict = self.get_auth_headers()
        
        pending_positions = self.get_all_pending_positions()
        
        url: str = f"{self.base_url}/trade/accounts/{self.account_id}/state"
        r = requests.get(url, headers=headers)
        json: dict = r.json()
        
        keys = self.api_mappings.account_status
        values = json["d"]["accountDetailsData"]
        account_state_dict = TradeLockerBroker.make_dict(keys, values)
        
        from_ms = int(date_from.timestamp() * 1000)
        to_ms = int(date_to.timestamp() * 1000)
        
        params = {
            "routeId": self.instrument.info_route_id,
            "from": from_ms,
            "to": to_ms,
            "tradableInstrumentId": self.instrument.tradable_id,
        }
        
        url: str = f"{self.base_url}/trade/accounts/{self.account_id}/ordersHistory"
        r = requests.get(url, params=params, headers=headers)
        json: dict = r.json()
        keys = self.api_mappings.orders_history_mappings
        
        if "d" not in json or "ordersHistory" not in json["d"]:
            raise RuntimeError(f"TraderLocker error: {json}")
        
        order_hist_data = json["d"]["ordersHistory"]
        
        trades = [Trade.from_tradelocker_order_history_row(values, keys) for values in order_hist_data]
        
        bid, ask = self.get_current_bid_ask()
        positions = Position.from_tradelocker_trades(trades=trades, instrument=self.instrument)
        
        gross_pnl = sum([p.gross_pnl for p in positions])
        net_pnl = sum([p.net_pnl for p in positions])
        
        return AccountSnapshot(
            cycle_open_gross_pnl=gross_pnl,
            cycle_open_net_pnl=net_pnl,
            account_open_gross_pnl=account_state_dict['openGrossPnL'],
            account_open_net_pnl=account_state_dict['openNetPnL'],
            account_balance=account_state_dict['balance'],
            account_projected_balance=account_state_dict['projectedBalance'],
            account_cash_balance=account_state_dict['cashBalance'],
            unsettled_cash=account_state_dict['unsettledCash'],
            activated_positions=positions,
            num_pending_positions = len(pending_positions)
        )
        
    
    def get_all_pending_positions(self):
        pending_positions = []
        headers: dict = self.get_auth_headers()
        headers['accountId'] = self.account_id
        headers['tradableInstrumentId'] = str(self.instrument.tradable_id)
        url: str = f"{self.base_url}/trade/accounts/{self.account_id}/orders"
        r = requests.get(url, headers=headers)
        keys = self.api_mappings.orders_mappings
        json: dict = r.json()
        if r.status_code != 200:
            t = 0
        orders = json["d"]["orders"]
        if orders:
            pending_positions = [Position.from_tradelocker_trades([Trade.from_tradelocker_order_history_row(o, keys) for o in orders], instrument=self.instrument)]
        return pending_positions
    
    
    def cancel_all_pending_positions(self):
        headers: dict = self.get_auth_headers()
        headers['accountId'] = self.account_id
        headers['tradableInstrumentId'] = str(self.instrument.tradable_id)
        url: str = f"{self.base_url}/trade/accounts/{self.account_id}/orders"
        r = requests.delete(url, headers=headers)
        r.status_code


    def close_all_active_positions(self) -> bool:
        headers = self.get_auth_headers()
        headers["accountId"] = self.account_id
        headers["tradableInstrumentId"] = str(self.instrument.tradable_id)

        url = f"{self.base_url}/trade/accounts/{self.account_id}/positions"
        requests.delete(url, headers=headers)

        while True:
            time.sleep(2)

            r = requests.get(url, headers=headers)
            json_data = r.json()
            positions = json_data["d"]["positions"]

            if len(positions) == 0:
                return True


    async def close_all(self) -> bool:
        # close all active positions:
        self.close_all_active_positions()
        
        # cancel all pending orders
        self.cancel_all_pending_positions()
        
        return True
    
    @staticmethod
    def make_dict(keys: List[str], values: List[Any]):
        dict = {keys[i]: values[i] for i in range(len(keys))}
        return dict
        
        
    # ----------------------------------------------------------------------
    # unimplemented
    # ---------------------------------------------------------------------- 
    
    def get_candles_range_from_csv(self):
        pass
    
    def place_market_buy(self):
        pass
    
    def close_trade(self):
        pass
    
    def get_open_trades(self):
        pass
    
    def get_active_cycle(self):
        pass
    
    def flatten_all(self):
        pass
    