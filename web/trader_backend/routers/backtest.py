from fastapi import APIRouter
from strategies.rules_based.rsi_lowrider.backtest import RSILowriderBacktester
from strategies.rules_based.rsi_lowrider.dto.backtest_results_dto import LowriderBacktestResultsDto
from strategies.rules_based.rsi_lowrider.strategy import RSILowriderConfig
from web.trader_backend.schemas.backtest import BacktestRequest, RsiLowriderBacktestRequest

router = APIRouter(prefix="/api/backtest", tags=["backtest"])


@router.post("/run", response_model=LowriderBacktestResultsDto)
async def run(request: RsiLowriderBacktestRequest):
    """
    Run an RSI-Lowrider backtest and return a full DTO time-series.
    """

    print("Received backtest request:", request.model_dump())

    config = RSILowriderConfig(
        rsi_period=request.rsi_period,
        rsi_oversold_level=request.rsi_oversold_level,
        rung_size_in_pips=request.rung_size_in_pips,
        tp_target_in_pips=request.tp_target_in_pips,
    )

    engine = RSILowriderBacktester(config=config)
    results: LowriderBacktestResultsDto = await engine.get_backtest_results(request)

    return results