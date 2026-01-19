"""Functions for working with worlds."""

from __future__ import annotations
import random
from tcod.ecs import Registry, Entity
from game.components import Gold, Graphic, Position, Fighter, IsMonster
from game.tags import IsActor, IsItem, IsPlayer
from .map_gen import generate_dungeon


# Registry "contains world and how it will be used"
def new_world(width: int, height: int) -> Registry:
    world = Registry()

    grid, rooms = generate_dungeon()

    for y in range(len(grid)):
        for x in range(len(grid[0])):
            if grid[y][x] == "#":
                wall = world[object()]
                wall.components[Position] = Position(x, y)
                wall.components[Graphic] = Graphic(ord("#"), fg=(120, 120, 120))
                wall.tags.add("Solid")

    player_x, player_y = rooms[0].center
    spawn_player(world, player_x, player_y)

    for i in range(10):
        random_room = random.choice(rooms[1:])
        monster_x = random.randint(random_room.x1, random_room.x2 - 1)
        monster_y = random.randint(random_room.y1, random_room.y2 - 1)
        spawn_monster(world, monster_x, monster_y)

    for i in range(15):
        random_room = random.choice(rooms[1:])
        gold_x = random.randint(random_room.x1, random_room.x2 - 1)
        gold_y = random.randint(random_room.y1, random_room.y2 - 1)
        spawn_gold(world, gold_x, gold_y)

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
    gold.components[Gold] = 5  # Or a random amount
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
