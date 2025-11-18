import pytest
from data.ingestion.tradelocker.client import TradeLockerClient
from data.models.candle import Candle

EURUSD_TID = 278   # tradableInstrumentId for EURUSD

@pytest.fixture(scope="module")
def client() -> TradeLockerClient:
    c = TradeLockerClient()
    token = c.authenticate()
    assert token is not None, "Failed to authenticate with TradeLocker"
    return c

def test_get_candles_returns_list_of_candles(client):
    candles = client.get_candles(
        tradable_id=EURUSD_TID,
        resolution="1m",
        minutes=2
    )

    # Basic checks
    assert isinstance(candles, list), "Expected a list"
    assert len(candles) > 0, "Expected at least one candle"

    # Check type of first candle
    first = candles[0]
    assert isinstance(first, Candle), "Elements should be Candle instances"

    # Check fields
    assert first.open is not None
    assert first.high is not None
    assert first.low is not None
    assert first.close is not None
    assert first.volume is not None

    # Check types
    assert isinstance(first.open, float)
    assert isinstance(first.high, float)
    assert isinstance(first.low, float)
    assert isinstance(first.close, float)
    assert isinstance(first.volume, float) or isinstance(first.volume, int)

    # Check timestamp
    assert first.timestamp is not None
    assert hasattr(first.timestamp, "year"), "timestamp should be a datetime object"

def test_candles_are_chronological(client):
    candles = client.get_candles(
        tradable_id=EURUSD_TID,
        resolution="1m",
        minutes=5
    )

    # Ensure ascending timestamps
    timestamps = [c.timestamp for c in candles]
    assert timestamps == sorted(timestamps), "Candles should be sorted by time ascending"
