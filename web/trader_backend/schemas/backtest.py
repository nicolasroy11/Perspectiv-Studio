from typing import Optional
from pydantic import BaseModel


class RSIConfig(BaseModel):
    enabled: bool
    period: Optional[int] = None


class EMACrossoverConfig(BaseModel):
    enabled: bool
    shortPeriod: Optional[int] = None
    longPeriod: Optional[int] = None


class RulesBasedConfig(BaseModel):
    rsi: RSIConfig
    emaCrossover: EMACrossoverConfig


class RLConfig(BaseModel):
    learningRate: float


class BacktestRequest(BaseModel):
    asset: str
    tradingType: str       # "rules-based" | "rl" | "llm"
    frequency: str         # "1m" | "5m" | etc.
    dateFrom: str          # we can make these dates later
    dateTo: str

    rulesBased: Optional[RulesBasedConfig] = None
    rl: Optional[RLConfig] = None
