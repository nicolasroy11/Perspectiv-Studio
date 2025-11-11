from fastapi import APIRouter, HTTPException
from pathlib import Path
import pandas as pd

router = APIRouter(prefix="/api/eval", tags=["eval"])

DATA_PATH = Path("data/eval/llm_decisions.parquet")

@router.get("/stats")
def get_eval_stats():
    if not DATA_PATH.exists():
        raise HTTPException(status_code=404, detail="Evaluation file not found")

    df = pd.read_parquet(DATA_PATH)
    if df.empty:
        raise HTTPException(status_code=400, detail="Evaluation file is empty")

    total = int(len(df))
    enter = int((df["action"] == "ENTER").sum())
    skip = int((df["action"] == "SKIP").sum())
    mean_confidence = float(df["confidence"].mean())

    stats = {
        "total": total,
        "enter": enter,
        "skip": skip,
        "enter_ratio": round(enter / total, 3) if total > 0 else 0.0,
        "mean_confidence": round(mean_confidence, 3),
    }

    return {k: (float(v) if isinstance(v, (pd.Series, pd.DataFrame)) else v) for k, v in stats.items()}
