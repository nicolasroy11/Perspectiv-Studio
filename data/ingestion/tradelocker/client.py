from datetime import datetime, timezone
import time
from typing import List
import requests
from data.models.candle import Candle
import runtime_settings as rs


class TradeLockerClient:
    def __init__(self, email: str = rs.TRADELOCKER_EMAIL, password: str = rs.TRADELOCKER_PASSWORD, server: str = rs.TRADELOCKER_SERVER):
        self.email = email
        self.password = password
        self.server = server
        self.base_url = rs.TRADELOCKER_BASE_API_URL
        self.token = None

    def authenticate(self):
        url = f"{self.base_url}/auth/jwt/token"

        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        payload = {
            "email": self.email,
            "password": self.password,
            "server": self.server
        }
        response = requests.post(url, json=payload, headers=headers)

        print(response.text)
        
        if response.status_code != 201:
            print("authentication failed:", response.text)
            return None
        
        data = response.json()
        self.token = data.get("accessToken")
        print("authenticated! Token acquired.")
        return self.token
    
    def get_all_accounts(self):
        if not self.token:
            raise RuntimeError("Authenticate first.")

        url = f"{self.base_url}/auth/jwt/all-accounts"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

        response = requests.get(url, headers=headers)
        print(response.text)

        if response.status_code != 200:
            raise RuntimeError(f"Failed to fetch accounts: {response.text}")

        return response.json()['accounts']
    
    def get_instruments(self, account_id: str):
        url = f"{self.base_url}/trade/accounts/{account_id}/instruments"

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "accNum": "1"
        }

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise RuntimeError(f"Failed to fetch instruments: {response.text}")

        return response.json()
    
    def get_candles(self, tradable_id: int, resolution: str = "1m", minutes: int = 60):
        url = f"{self.base_url}/trade/history"

        now = int(time.time() * 1000)          # current time in ms
        from_ts = now - minutes * 60 * 1000   # lookback window

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "accNum": "1"                     # REQUIRED
        }

        params = {
            "routeId": "452",                 # INFO route for all instruments
            "from": from_ts,
            "to": now,
            "resolution": resolution,         # EXACT ENUM: "1m", "5m", "15m", "1H", etc
            "tradableInstrumentId": tradable_id
        }

        r = requests.get(url, headers=headers, params=params)
        print("DEBUG:", r.text)

        if r.status_code != 200:
            raise RuntimeError(f"Failed: {r.text}")

        raw = r.json()
        return self.convert_history_response_to_candles(raw)

    def convert_history_response_to_candles(self, data: dict) -> List[Candle]:
        if "barDetails" in data:
            bars = data["barDetails"]
        elif "d" in data and isinstance(data["d"], dict) and "barDetails" in data["d"]:
            bars = data["d"]["barDetails"]
        else:
            raise ValueError(
                f"History response missing 'barDetails'. Top-level keys: {list(data.keys())}"
            )

        candles: List[Candle] = []

        for bar in bars:
            ts = bar["t"]
            dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)

            candles.append(
                Candle(
                    timestamp=dt,
                    open=bar["o"],
                    high=bar["h"],
                    low=bar["l"],
                    close=bar["c"],
                    volume=bar.get("v", 0.0),
                )
            )

        return candles


client = TradeLockerClient()
client.authenticate()
acc = client.get_all_accounts()
inst = client.get_instruments(acc[0]['id'])

eurusd_tid = 278
candles = client.get_candles(tradable_id=eurusd_tid, resolution="1m", minutes=120)
y = 0