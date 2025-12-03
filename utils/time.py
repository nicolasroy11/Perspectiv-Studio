from datetime import datetime, timezone

def ms_to_dt(ms: str | int) -> datetime:
    return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc)