from data.ingestion.tradelocker.client import TradeLockerClient
import runtime_settings as rs

def test_auth():
    EMAIL = rs.TRADELOCKER_EMAIL
    PASSWORD = rs.TRADELOCKER_PASSWORD
    SERVER = rs.TRADELOCKER_SERVER  # e.g. "AtlasFunded-Live" or whatever TL shows

    client = TradeLockerClient(
        email=EMAIL,
        password=PASSWORD,
        server=SERVER
    )

    token = client.authenticate()

    assert token is not None, "authentication failed — token was None"
    assert isinstance(token, str), "token should be a string"

    print("test passed — JWT acquired:", token[:20], "...")
