from dataclasses import dataclass

from models.position import Position


@dataclass
class Cycle:
    symbol: str
    positions: list[Position]

