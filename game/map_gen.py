import random
from game.constants import SCREEN_HEIGHT, SCREEN_WIDTH
import attrs

TILE_WALL = "#"
TILE_FLOOR = "."

MIN_ROOM_WIDTH = 4
MAX_ROOM_WIDTH = 12
MIN_ROOM_HEIGHT = 4
MAX_ROOM_HEIGHT = 10
MAX_ROOM_ATTEMPTS = 25

@attrs.define(frozen=True)
class Rect:
    x1: int
    y1: int
    x2: int
    y2: int

    @classmethod
    def from_dimensions(cls, x: int, y: int, w: int, h: int) -> "Rect":
        return cls(x1=x, y1=y, x2=x+w, y2=y+h)

    # Implement Midoint formula to find center
    @property
    def center(self) -> tuple[int, int]:
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return(center_x, center_y)

    def intersects(self, other: "Rect") -> bool:
        return (
            self.x1 <= other.x2 and
            self.x2 >= other.x1 and
            self.y1 <= other.y2 and
            self.y2 >= other.y1
        )

def generate_dungeon() -> tuple[list[list[str]], list[Rect]]:
        rooms = []
        grid = [["#" for x in range(SCREEN_WIDTH)] for y in range(SCREEN_HEIGHT)]

        for i in range(MAX_ROOM_ATTEMPTS):
            w = random.randint(MIN_ROOM_WIDTH, MAX_ROOM_WIDTH)
            h = random.randint(MIN_ROOM_HEIGHT, MAX_ROOM_HEIGHT)

            x = random.randint(1, SCREEN_WIDTH - w - 1)
            y = random.randint(1, SCREEN_HEIGHT - h - 1)

            rec = Rect.from_dimensions(x, y, w, h)

            collision = False
            for room in rooms:
                if rec.intersects(room):
                    collision = True
                    break
            if not collision:
                for y in range(rec.y1, rec.y2):
                    for x in range(rec.x1, rec.x2):
                        grid[y][x] = "."
                rooms.append(rec)
        for i in range(1, len(rooms)):
            # Get coords for previous and current room
            prev_x, prev_y = rooms[i-1].center
            new_x, new_y = rooms[i].center

            # Draw L corridor
            if random.randint(0, 1) == 1:
                # Horizontal then vertical
                for x in range(min(prev_x, new_x), max(prev_x, new_x) + 1):
                    grid[prev_y][x] = "."
                for y in range(min(prev_y, new_y), max(prev_y, new_y) + 1):
                    grid[y][new_x] = "."
            else:
                # Vertical then horizontal
                for y in range(min(prev_y, new_y), max(prev_y, new_y) + 1):
                    grid[y][prev_x] = "."
                for x in range(min(prev_x, new_x), max(prev_x, new_x) + 1):
                    grid[new_y][x] = "."
        # start_x, start_y = rooms[0].center
        # grid[start_y][start_x] = "@"
        # end_x, end_y = rooms[-1].center
        # grid[end_y][end_x] = ">"
        # for row in grid:
        #     print("".join(row))
        # In generate_dungeon(), before return:
        for i, room in enumerate(rooms):
            print(f"Room {i}: x1={room.x1}, y1={room.y1}, x2={room.x2}, y2={room.y2}")
        return grid, rooms



# grid, rooms = generate_dungeon()

# for y in range(len(grid)):
#     for x in range(len(grid[0])):
#         if grid[y][x] == "#":
#             wall = world[object()]
#             wall.components[Position] = Position(x, y)
#             wall.components[Graphic] = Graphic(ord("#"), fg=(120, 120, 120))
#             wall.tags.add("Solid")
#     # if grid[y][x] equals "#"
#         # create a "wall #"


