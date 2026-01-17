"""Functions for working with worlds."""

from __future__ import annotations
from random import Random
from tcod.ecs import Registry
from game.components import Gold, Graphic, Position
from game.tags import IsActor, IsItem, IsPlayer

# Registry "contains world and how it will be used"
def new_world(width: int, height: int) -> Registry:
    world = Registry()

    x_min, x_max = 1, width - 2
    y_min, y_max = 1, height - 5

    # Create one unique random number generator for the world
    rng = world[None].components[Random] = Random()

    # Create player
    player = world[object()]
    player.components[Position] = Position(width // 2, height // 2)
    player.components[Graphic] = Graphic(ord("@"))
    player.components[Gold] = 0
    player.tags |= {IsPlayer, IsActor}

    # Scatter gold around the world randomly
    for _ in range(20):
        gold = world[object()]
        # Subtract 1 because randint() is inclusive and grid is zero-indexed
        x = rng.randint(x_min + 1, x_max - 1)
        y = rng.randint(y_min + 1, y_max - 1)

        gold.components[Position] = Position(x, y)
        gold.components[Graphic] = Graphic(ord("$"), fg=(255, 255, 0))
        gold.components[Gold] = rng.randint(1, 10)
        gold.tags |= {IsItem}



    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            if x == x_min or x == x_max or y == y_min or y == y_max:
                wall = world[object()]
                wall.components[Position] = Position(x, y)
                wall.components[Graphic] = Graphic(ord("#"), fg=(120, 120, 120))
                wall.tags.add("Solid")

    return world
