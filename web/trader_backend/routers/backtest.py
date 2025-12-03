from fastapi import APIRouter
from strategies.rules_based.rsi_lowrider.backtest import RSILowriderBacktester
from strategies.rules_based.rsi_lowrider.dto.backtest_results_dto import LowriderBacktestResultsDto
from web.trader_backend.schemas.backtest import BacktestRequest, RsiLowriderBacktestRequest

router = APIRouter(prefix="/api/backtest", tags=["backtest"])


@router.post("/run", response_model=LowriderBacktestResultsDto)
async def run(request: RsiLowriderBacktestRequest):
    """
    Run an RSI-Lowrider backtest and return a full DTO time-series.
    """

    print("Received backtest request:", request.model_dump())

    engine = RSILowriderBacktester()
    results: LowriderBacktestResultsDto = await engine.get_backtest_results(request)

    return results