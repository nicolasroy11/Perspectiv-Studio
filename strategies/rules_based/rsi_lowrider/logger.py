from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Any


class BacktestLogger:
    """
    Lightweight JSONL logger.
    Each event is a JSON object appended to the log file.
    """

    def __init__(self, path: str):
        self.path = path

        # wipe previous runs
        with open(self.path, "w") as f:
            f.write("")

    def log(self, event: str, **data: Any):
        """Write one structured event line."""
        record = {
            "ts": datetime.now(tz=timezone.utc).isoformat(),
            "event": event,
        }
        record.update(data)

        with open(self.path, "a") as f:
            f.write(json.dumps(record) + "\n")
