from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.alias_generators import to_camel


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
    frequency: str         # "1m" | "5m" | etc.
    date_from: datetime = Field(alias="dateFrom")
    date_to: datetime = Field(alias="dateTo")
    
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,   # REQUIRED for Python-side snake_case for some reason
    )
    
    @field_validator("date_from", "date_to", mode="plain")
    def ensure_timezone(cls, v):
        # Accept either raw datetime or ISO string
        if isinstance(v, datetime):
            dt = v
        else:
            dt = datetime.fromisoformat(v)

        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt
    
class RsiLowriderBacktestRequest(BacktestRequest):
    rsi_period: int = Field(alias="rsiPeriod")
    rsi_oversold_level: int = Field(alias="rsiOversoldLevel")
    rung_size_in_pips: float = Field(alias="rungSizeInPips")
    tp_target_in_pips: float = Field(alias="tpTargetInPips")
        
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )