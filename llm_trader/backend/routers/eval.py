from fastapi import APIRouter, HTTPException
from pathlib import Path
import pandas as pd

router = APIRouter()

DATA_PATH = Path("data/eval/llm_decisions.parquet")

@router.get("/eval")
def get_eval_data(limit: int = 2000):
    """Return LLM evaluation results (action, confidence, rationale)."""
    if not DATA_PATH.exists():
        raise HTTPException(status_code=404, detail="Evaluation file not found.")
    df = pd.read_parquet(DATA_PATH)

    # Basic sanity clamp
    limit = min(limit, len(df))
    records = df.head(limit).to_dict(orient="records")
    return {"count": len(records), "data": records}
