from pathlib import Path
from fastapi.testclient import TestClient
from web.backend.main import app
from web.backend.routers import eval as eval_router

client = TestClient(app)

def test_eval_endpoint_ok(monkeypatch, tmp_path):
    # Fake parquet
    import pandas as pd
    df = pd.DataFrame([
        {"end_time": "2024-01-01", "action": "ENTER", "confidence": 0.9, "rationale": "mock"}
    ])
    p = tmp_path / "llm_decisions.parquet"
    df.to_parquet(p)
    
    
    monkeypatch.setattr(eval_router, "DATA_PATH", p)
    
    r = client.get("/api/eval")
    assert r.status_code == 200
    data = r.json()
    assert "count" in data and "data" in data
    assert data["count"] == 1
    assert data["data"][0]["action"] == "ENTER"

def test_eval_not_found(monkeypatch):
    from web.backend.routers import eval as eval_router
    monkeypatch.setattr(eval_router, "DATA_PATH", Path("nonexistent.parquet"))
    r = client.get("/api/eval")
    assert r.status_code == 404
