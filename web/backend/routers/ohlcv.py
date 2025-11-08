# llm_trader/backend/routers/ohlcv.py
from fastapi import APIRouter, HTTPException
from pathlib import Path
import pandas as pd

router = APIRouter()

DATA_PATH = Path("llm_trader/experiments/eurusd_5m.csv")

@router.get("/ohlcv")
def get_ohlcv(limit: int = 5000):
    """Return historical OHLCV candles."""
    if not DATA_PATH.exists():
        raise HTTPException(status_code=404, detail="Price data file not found.")
    df = pd.read_csv(DATA_PATH)
    df = df.head(limit)
    return {"count": len(df), "data": df.to_dict(orient="records")}
