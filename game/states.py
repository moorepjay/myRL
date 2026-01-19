from __future__ import annotations

import attrs
import tcod.console
import tcod.event
import time


import g
from game.components import Gold, Graphic, Position, Fighter, IsMonster
from game.tags import IsItem, IsPlayer
from .menu import ListMenu, SelectItem
from .world_tools import new_world
from .constants import DIRECTION_KEYS
from .state import StateResult, Reset, State, Push
from .constants import SCREEN_HEIGHT, SCREEN_WIDTH
from tcod.event import KeySym


class MainMenu(ListMenu):
    """Main/escape menu."""

    __slots__ = ()

    def __init__(self) -> None:
        """Initialize the main menu."""
        items = [
            SelectItem("New game", self.new_game),
            SelectItem("Quit", self.quit),
        ]
        if hasattr(g, "world"):
            items.insert(0, SelectItem("Continue", self.continue_))

        super().__init__(
            items=tuple(items),
            selected=0,
            x=5,
            y=5,
        )

    @staticmethod
    def continue_() -> StateResult:
        """Return to the game."""
        return Reset(InGame())

    @staticmethod
    def new_game() -> StateResult:
        """Begin a new game."""
        g.world = new_world(SCREEN_WIDTH, SCREEN_HEIGHT)
        return Reset(InGame())

    @staticmethod
    def quit() -> StateResult:
        """Close the program."""
        raise SystemExit


@attrs.define()
class InGame(State):
    """Primary in-game state."""

    last_move_time: float = 0.0
    move_delay: float = 0.12

    def on_event(self, event: tcod.event.Event) -> StateResult:
        """Move the player on events and handle exiting."""
        (player,) = g.world.Q.all_of(tags=[IsPlayer])
        match event:
            case tcod.event.Quit():
                raise SystemExit

            case tcod.event.KeyDown(sym=sym) if sym in DIRECTION_KEYS:
                current_time = time.time()
                if current_time - self.last_move_time < self.move_delay:
                    return None

                target_pos = player.components[Position] + DIRECTION_KEYS[sym]
                print(f"Trying to move to: {target_pos}")

                target_entities = list(
                    g.world.Q.all_of(components=[Fighter], tags=[target_pos])
                )
                print(f"Entities at target: {len(target_entities)}")

                solid_check = list(g.world.Q.all_of(tags=[target_pos, "Solid"]))
                print(f"Solid entities at target: {len(solid_check)}")  # Add this
                if target_entities:
                    target = target_entities[0]
                    self.resolve_combat(player, target)

                    player_message = g.world[None].components.get(("Text", str), "")

                    if (
                        target.components.get(Fighter)
                        and target.components[Fighter].hp > 0
                    ):
                        self.resolve_combat(target, player)

                        monster_message = g.world[None].components.get(
                            ("Text", str), ""
                        )

                        combined = f"{player_message} {monster_message}"
                        g.world[None].components[("Text", str)] = combined

                    self.last_move_time = current_time

                elif not g.world.Q.all_of(tags=[target_pos, "Solid"]):
                    player.components[Position] = target_pos
                    self.last_move_time = current_time

                    # Auto pickup gold
                    for gold in g.world.Q.all_of(
                        components=[Gold], tags=[player.components[Position], IsItem]
                    ):
                        player.components[Gold] += gold.components[Gold]
                        text = f"Picked up {gold.components[Gold]}g, total: {player.components[Gold]}g"
                        g.world[None].components[("Text", str)] = text
                        gold.clear()
                else:
                    g.world[None].components[("Text", str)] = (
                        "This is definitely a solid object."
                    )

                return None

            # Print coords for debugging
            case tcod.event.MouseMotion(tile=(x, y)):
                # This prints the current 'Ordered Pair' to your terminal
                print(f"Mouse at Coordinate: ({x}, {y})")
                return None
            case tcod.event.KeyDown(sym=KeySym.ESCAPE):
                return Push(MainMenu())
            case _:
                return None

    def on_draw(self, console: tcod.console.Console) -> None:
        """Draw entities."""

        (player,) = g.world.Q.all_of(tags=[IsPlayer])
        pos = player.components[Position]
        print(f"Player position: {pos.x}, {pos.y}")

        for entity in g.world.Q.all_of(components=[Position, Graphic]):
            pos = entity.components[Position]
            # Guard against out of bounds positions
            if not (0 <= pos.x < console.width and 0 <= pos.y < console.height):
                continue
            graphic = entity.components[Graphic]
            console.rgb[["ch", "fg"]][pos.y, pos.x] = graphic.ch, graphic.fg

        if text := g.world[None].components.get(("Text", str)):
            console.print(
                x=0, y=console.height - 1, text=text, fg=(255, 255, 255), bg=(0, 0, 0)
            )

        # Draw coordinate compass
        (player,) = g.world.Q.all_of(tags=[IsPlayer])
        pos = player.components[Position]

        compass_text = f"Location: ({pos.x}, {pos.y})"
        x_pos = console.width - len(compass_text)

        console.print(
            x=x_pos,
            y=console.height - 1,
            text=compass_text,
            fg=(255, 255, 255),
            bg=(50, 50, 50),
        )

    def resolve_combat(
        self, attacker: tcod.ecs.Entity, defender: tcod.ecs.Entity
    ) -> None:
        """Handle a combat exchange between two entities."""
        a_stats = attacker.components[Fighter]
        d_stats = defender.components[Fighter]

        # Damage = Power - Defense (Min 0)
        damage = max(0, a_stats.power - d_stats.defense)
        new_hp = d_stats.hp - damage

        # Update defender stats (replacing the frozen dataclass)
        defender.components[Fighter] = Fighter(
            hp=new_hp,
            max_hp=d_stats.max_hp,
            power=d_stats.power,
            defense=d_stats.defense,
        )

        if IsPlayer in attacker.tags:
            # Player attacking something
            name = "Monster" if IsMonster in defender.tags else "Something"
        else:
            # Something attacking player
            name = "Monster" if IsMonster in attacker.tags else "Something"

        # Log to the on-screen message bar
        if IsPlayer in attacker.tags:
            if new_hp <= 0:
                message = f"You kill the {name}!"
            else:
                message = f"You hit the {name} for {damage} HP."
        else:
            # Something is attacking the player
            if new_hp <= 0:
                message = "YOU HAVE BEEN SLAIN!"
            else:
                message = f"{name} strikes you for {damage}!"

        g.world[None].components[("Text", str)] = message

        if new_hp <= 0:
            defender.clear()
