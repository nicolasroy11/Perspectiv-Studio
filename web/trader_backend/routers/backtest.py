from fastapi import APIRouter
from web.trader_backend.schemas.backtest import BacktestRequest

router = APIRouter(prefix="/api/backtest", tags=["backtest"])

@router.post("/run")
async def run_backtest(request: BacktestRequest):
    print("Received backtest request:", request.model_dump())

    return {
        "status": "ok",
        "message": "Backtest request received",
        "received": request.model_dump(),
    }
