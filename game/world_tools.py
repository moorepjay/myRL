"""Functions for working with worlds."""

from __future__ import annotations
from random import Random
from tcod.ecs import Registry, Entity
from game.components import Gold, Graphic, Position, Fighter, IsMonster
from game.tags import IsActor, IsItem, IsPlayer

# Registry "contains world and how it will be used"
def new_world(width: int, height: int) -> Registry:
    world = Registry()

    x_min, x_max = 1, width - 2
    y_min, y_max = 1, height - 5

    # Create perimeter wall
    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            if x == x_min or x == x_max or y == y_min or y == y_max:
                wall = world[object()]
                wall.components[Position] = Position(x, y)
                wall.components[Graphic] = Graphic(ord("#"), fg=(120, 120, 120))
                wall.tags.add("Solid")

    # Create one unique random number generator for the world
    rng = world[None].components[Random] = Random()

    # Create player
    spawn_player(world, width // 2, height // 2)

    # Scatter gold around the world randomly
    for _ in range(20):
        gold = world[object()]
        # Subtract 1 because randint() is inclusive and grid is zero-indexed
        x = rng.randint(x_min + 1, x_max - 1)
        y = rng.randint(y_min + 1, y_max - 1)
        spawn_gold(world, x, y)

    # Create monster
    spawn_monster(world, 15, 15)

    return world

def spawn_player(world: Registry, x: int, y: int) -> Entity:
    player = world[object()]
    player.components[Position] = Position(x, y)
    player.components[Graphic] = Graphic(ord("@"), fg=(255, 255, 255))
    player.components[Gold] = 0
    player.components[Fighter] = Fighter(hp=30, max_hp=30, power=5, defense=2)
    player.tags.add(IsPlayer)
    return player

def spawn_gold(world: Registry, x: int, y: int) -> Entity:
    gold = world[object()]
    gold.components[Position] = Position(x, y)
    gold.components[Graphic] = Graphic(ord("$"), fg=(255, 255, 0))
    gold.components[Gold] = 5 # Or a random amount
    gold.tags.add(IsItem)
    return gold

def spawn_monster(world: Registry, x: int, y: int):
    monster = world[object()]
    monster.components[Position] = Position(x, y)
    monster.components[Graphic] = Graphic(ord("M"), fg=(255, 0, 0))

    # Capabilities: It can fight
    monster.components[Fighter] = Fighter(hp=10, max_hp=10, power=3, defense=1)

    # Identity: It is a monster (useful for AI or player-targeting)
    monster.tags.add(IsMonster)
    monster.tags.add("Solid")
    return monster

