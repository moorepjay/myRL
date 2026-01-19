from __future__ import annotations

import tcod.console
import tcod.event
import tcod.context
import tcod.tileset

import game.states
import game.world_tools
import game.state_tools
import g
from game.constants import SCREEN_WIDTH, SCREEN_HEIGHT


def main() -> None:
    """Load a tileset and open a window using it."""
    tileset = tcod.tileset.load_tilesheet(
        "src/data/Alloy_curses_12x12.png",
        columns=16,
        rows=16,
        charmap=tcod.tileset.CHARMAP_CP437,
    )
    tcod.tileset.procedural_block_elements(tileset=tileset)
    g.console = tcod.console.Console(SCREEN_WIDTH, SCREEN_HEIGHT)
    g.states = [game.states.MainMenu()]
    with tcod.context.new(
        console=g.console,
        tileset=tileset,
        sdl_window_flags=tcod.context.SDL_WINDOW_RESIZABLE
        | tcod.context.SDL_WINDOW_MAXIMIZED,
    ) as g.context:
        game.state_tools.main_loop()


if __name__ == "__main__":
    main()
