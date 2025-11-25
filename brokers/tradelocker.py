from __future__ import annotations

import time
import requests
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import runtime_settings as rs
from models.candle import Candle
from models.position import Position
from models.trade import Trade, Side
from brokers.base import BaseBroker


@dataclass
class InstrumentInfo:
    symbol: str
    tradable_id: int


class TradeLockerBroker(BaseBroker):
    """
    Unified TradeLocker interface.
    This single class handles:
      - Authentication
      - Account and instrument lookup
      - Candle history
      - Market and limit order placement
      - Adding rungs (limit buy with corresponding TP)
      - Flattening positions
      - Mapping TL API -> internal models (Candle, Trade, Position)

    This replaces the old TradeLockerClient and the old Broker wrapper entirely.
    """

    def __init__(
        self,
        email: str = rs.TRADELOCKER_EMAIL,
        password: str = rs.TRADELOCKER_PASSWORD,
        server: str = rs.TRADELOCKER_SERVER,
        base_url: str = rs.TRADELOCKER_BASE_API_URL,
        account_id: Optional[str] = None,
    ):
        self.email = email
        self.password = password
        self.server = server
        self.base_url = base_url

        self.token: Optional[str] = None
        self.account_id = account_id

        # symbol -> tradable_id
        self._instrument_map: dict[str, int] = {}

        self.authenticate()
        if self.account_id is None:
            self._auto_assign_account()

        # Load instruments once
        self._load_instruments()

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

    def _auth_headers(self):
        if not self.token:
            raise RuntimeError("Not authenticated")
        return {
            "accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "accNum": "1",
        }

    # ----------------------------------------------------------------------
    # Account / instrument discovery
    # ----------------------------------------------------------------------
    def _auto_assign_account(self):
        url = f"{self.base_url}/auth/jwt/all-accounts"
        r = requests.get(url, headers=self._auth_headers())

        if r.status_code != 200:
            raise RuntimeError(f"Could not fetch accounts: {r.text}")

        accounts = r.json()["accounts"]
        if not accounts:
            raise RuntimeError("No TL accounts available")

        self.account_id = accounts[0]["id"]

    def _load_instruments(self):
        url = f"{self.base_url}/trade/accounts/{self.account_id}/instruments"
        r = requests.get(url, headers=self._auth_headers())
        if r.status_code != 200:
            raise RuntimeError(f"Could not fetch instruments: {r.text}")

        instruments = r.json()
        self._instrument_map = {item["symbol"]: item["tradableInstrumentId"] for item in instruments}

    def _get_tradable_id(self, symbol: str) -> int:
        if symbol not in self._instrument_map:
            raise KeyError(f"Symbol {symbol} not found in TL instruments.")
        return self._instrument_map[symbol]

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

        tradable_id = self._get_tradable_id(symbol)

        if date_from.tzinfo is None:
            date_from = date_from.replace(tzinfo=timezone.utc)
        if date_to.tzinfo is None:
            date_to = date_to.replace(tzinfo=timezone.utc)

        from_ms = int(date_from.timestamp() * 1000)
        to_ms = int(date_to.timestamp() * 1000)

        url = f"{self.base_url}/trade/history"
        params = {
            "routeId": "452",
            "from": from_ms,
            "to": to_ms,
            "resolution": resolution,
            "tradableInstrumentId": tradable_id,
        }

        r = requests.get(url, headers=self._auth_headers(), params=params)
        if r.status_code != 200:
            raise RuntimeError(f"Failed to fetch candles: {r.text}")

        return self._convert_bars_to_candles(r.json())

    def _convert_bars_to_candles(self, data: dict) -> List[Candle]:
        if "barDetails" in data:
            bars = data["barDetails"]
        elif "d" in data and "barDetails" in data["d"]:
            bars = data["d"]["barDetails"]
        else:
            raise ValueError(f"Invalid TL candle schema: {data}")

        out: List[Candle] = []
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

    # ----------------------------------------------------------------------
    # Order Placement
    # ----------------------------------------------------------------------
    def place_market_order(
        self,
        symbol: str,
        side: Side,
        lot_size: float,
        tp_price: Optional[float] = None,
        sl_price: Optional[float] = None,
        ladder_position: int = 0,
    ) -> Trade:
        """
        PLACE MARKET ORDER
        """
        # TODO: Fill with TL’s real endpoint once you capture it.
        raise NotImplementedError("Implement TL market order endpoint")

    def place_limit_order(
        self,
        symbol: str,
        side: Side,
        lot_size: float,
        limit_price: float,
        tp_price: Optional[float] = None,
        sl_price: Optional[float] = None,
        ladder_position: int = 0,
    ) -> Trade:
        """
        PLACE LIMIT ORDER (pending)
        """
        # TODO: Fill with TL’s real endpoint.
        raise NotImplementedError("Implement TL limit order endpoint")

    def add_rung(
        self,
        symbol: str,
        side: Side,
        lot_size: float,
        limit_price: float,
        tp_price: float,
        ladder_position: int,
    ) -> Trade:
        """
        Add a rung = limit buy + fixed TP 2 pips above.
        Limit order enters → TP placed immediately.
        """
        return self.place_limit_order(
            symbol=symbol,
            side=side,
            lot_size=lot_size,
            limit_price=limit_price,
            tp_price=tp_price,
            ladder_position=ladder_position,
        )

    # ----------------------------------------------------------------------
    # Position Control
    # ----------------------------------------------------------------------
    def close_position_market(self, position_id: str) -> None:
        """
        Flatten at market.
        """
        # TODO implement TL endpoint
        raise NotImplementedError("Implement TL close position endpoint")

    def refresh_position_snapshot(self, position_id: str) -> Position:
        """
        Fetch most recent TL position state.
        """
        # TODO implement TL endpoint
        raise NotImplementedError("Implement TL position snapshot endpoint")
    
    # ----------------------------------------------------------------------
    # unimplemented
    # ---------------------------------------------------------------------- 
    
    def get_candles_range_from_csv(self):
        pass
    
    def place_market_buy(self):
        pass

    def place_limit_buy(self):
        pass
    
    def close_trade(self):
        pass
    
    def get_open_trades(self):
        pass
    
    def get_active_position(self):
        pass
    
    def flatten_all(self):
        pass
    

# client = TradeLockerBroker()
# client.authenticate()
# inst = client._instrument_map

# # eurusd_tid = 278
# candles = client.get_candles(symbol="EURUSD", resolution="1m", minutes=1220)
# y = 0