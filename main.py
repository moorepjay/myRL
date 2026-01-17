from __future__ import annotations

import tcod.console
import tcod.event
import tcod.context
import tcod.tileset
import attrs

import g

@attrs.define()
class ExampleState:
    """Example with hard-coded player position."""

    player_x: int
    player_y: int

    def on_draw(self, console: tcod.console.Console) -> None:
        """Draw player."""
        console.print(self.player_x, self.player_y, "@")

    def on_event(self, event: tcod.event.Event) -> None:
        """Move the player on events and handle exiting. Movement is hard-coded"""
        match event:
            case tcod.event.Quit():
                raise SystemExit
            case tcod.event.KeyDown(sym=tcod.event.KeySym.LEFT):
                self.player_x -= 1
            case tcod.event.KeyDown(sym=tcod.event.KeySym.RIGHT):
                self.player_x += 1
            case tcod.event.KeyDown(sym=tcod.event.KeySym.DOWN):
                self.player_y += 1
            case tcod.event.KeyDown(sym=tcod.event.KeySym.UP):
                self.player_y -= 1


def main() -> None:
    """Load a tileset and open a window using it, it will close immediately."""
    tileset = tcod.tileset.load_tilesheet(
        "src/data/Alloy_curses_12x12.png", columns=16, rows=16, charmap=tcod.tileset.CHARMAP_CP437
    )
    tcod.tileset.procedural_block_elements(tileset=tileset)
    console = tcod.console.Console(80, 50)
    state = ExampleState(player_x=console.width // 2, player_y=console.height // 2)
    with tcod.context.new(console=console, tileset=tileset) as g.context:
        while True:
            console.clear()
            state.on_draw(console)
            g.context.present(console)
            for event in tcod.event.wait():
                print(event)
                if isinstance(event, tcod.event.Quit):
                    raise SystemExit
                state.on_event(event)

if __name__ == "__main__":
    main()