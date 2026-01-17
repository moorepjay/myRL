import attrs
import tcod.ecs.callbacks
from tcod.ecs import Entity
from typing import Final, Self

@attrs.define(frozen=True)
class Position:
    """An entities postion."""
    x: int
    y: int

    def __add__(self, direction: tuple[int, int]) -> Self:
        """Add a vector to this postion"""
        x, y = direction
        return self.__class__(self.x + x, self.y + y)

@attrs.define(frozen=True)
class Graphic:
    """An entities icon and color."""
    ch: int = ord("!")
    fg: tuple[int, int, int] = (255, 255, 255)

# Decorator is "watching" components for changes
@tcod.ecs.callbacks.register_component_changed(component=Position)
def on_position_changed(entity: Entity, old: Position | None, new: Position | None) -> None:
    """Mirror posistion components as a tag"""
    # Position hasn't changed, ignore
    if old == new:
        return
    # Position changed or was removed
    if old is not None:
        # Remove old position (can't be two places at once)
        entity.tags.discard(old)
    # If there is a new position for the entity
    if new is not None:
        # Add new position to tags
        entity.tags.add(new)


Gold: Final = ("Gold", int)
"""Amount of gold"""
