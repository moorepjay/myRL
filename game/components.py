import attrs
from typing import Self

@attrs.define(frozen=True)
class Position:
    """An entities postion."""

    x: int
    y: int

    def __add__(self, direction: tuple[int, int]) -> Self:
        """Add a vector to this postion"""
        x, y = direction
        return self.__class__(self.x + x, self.y + y)