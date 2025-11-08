from pathlib import Path
from fastapi.testclient import TestClient
from web.backend.main import app
import pandas as pd

client = TestClient(app)

def test_ohlcv_endpoint_ok(monkeypatch, tmp_path):
    csv = tmp_path / "ohlcv.csv"
    pd.DataFrame([
        {"timestamp": "2024-01-01", "open": 1.1, "high": 1.2, "low": 1.0, "close": 1.15}
    ]).to_csv(csv, index=False)

    from web.backend.routers import ohlcv as ohlcv_router
    monkeypatch.setattr(ohlcv_router, "DATA_PATH", csv)

    r = client.get("/api/ohlcv")
    assert r.status_code == 200
    data = r.json()
    assert "data" in data
    assert "timestamp" in data["data"][0]
    assert "open" in data["data"][0]

def test_ohlcv_not_found(monkeypatch):
    from web.backend.routers import ohlcv as ohlcv_router
    monkeypatch.setattr(ohlcv_router, "DATA_PATH", Path("missing.csv"))
    r = client.get("/api/ohlcv")
    assert r.status_code == 404
