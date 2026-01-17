from __future__ import annotations

import attrs
import tcod.console
import tcod.event


import g
from game.components import Gold, Graphic, Position
from game.constants import DIRECTION_KEYS
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
    def on_event(self, event: tcod.event.Event) -> StateResult:
        """Move the player on events and handle exiting."""
        (player,) = g.world.Q.all_of(tags=[IsPlayer])
        match event:
            case tcod.event.Quit():
                raise SystemExit
            case tcod.event.KeyDown(sym=sym) if sym in DIRECTION_KEYS:

                # Gaurd check for being in bounds
                target_pos = player.components[Position] + DIRECTION_KEYS[sym]
                if not g.world.Q.all_of(tags=[target_pos, "Solid"]):
                    player.components[Position] = target_pos
                    # Auto pickup gold
                    for gold in g.world.Q.all_of(components=[Gold], tags=[player.components[Position], IsItem]):
                        player.components[Gold] += gold.components[Gold]
                        text = f"Picked up {gold.components[Gold]}g, total: {player.components[Gold]}g"
                        g.world[None].components[("Text", str)] = text
                        gold.clear()
                else:
                    g.world[None].components[("Text", str)] = "This is definitely a solid object."

                return None

            # Print coords for debugging
            case tcod.event.MouseMotion(tile=(x, y)):
                # This prints the current 'Ordered Pair' to your terminal
                print(f"Mouse at Coordinate: ({x}, {y})")
                return None


                return None
            case tcod.event.KeyDown(sym=KeySym.ESCAPE):
                return Push(MainMenu())
            case _:
                return None

    def on_draw(self, console: tcod.console.Console) -> None:
        """Draw entities."""
        for entity in g.world.Q.all_of(components=[Position, Graphic]):
            pos = entity.components[Position]
            # Guard against out of bounds positions
            if not (0 <= pos.x < console.width and 0 <= pos.y < console.height):
                continue
            graphic = entity.components[Graphic]
            console.rgb[["ch", "fg"]][pos.y, pos.x] = graphic.ch, graphic.fg

        if text := g.world[None].components.get(("Text", str)):
            console.print(x=0, y=console.height -1, text=text, fg=(255,255,255), bg=(0, 0, 0))


