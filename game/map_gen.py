import random
from game.constants import (
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    MAP_MARGIN,
    MAP_HEIGHT,
    MAP_WIDTH,
)
import attrs

# Created constants in this file as there should no other module that requires their values.
TILE_WALL = "#"
TILE_FLOOR = "."

MIN_ROOM_WIDTH = 4
MAX_ROOM_WIDTH = 12
MIN_ROOM_HEIGHT = 4
MAX_ROOM_HEIGHT = 10
MAX_ROOM_ATTEMPTS = 25


# Rectangle class used in generating our dungeon created as immutable with attrs.
@attrs.define(frozen=True)
class Rect:
    x1: int
    y1: int
    x2: int
    y2: int

    # Classmethod that calculates and sets our rectangles dimensions. This was the cleanest way to
    # accomplish this while using attrs.
    @classmethod
    def from_dimensions(cls, x: int, y: int, w: int, h: int) -> "Rect":
        return cls(x1=x, y1=y, x2=x + w, y2=y + h)

    # Implement Midoint formula to find center. I don't know why its @property and not just a
    # function.
    @property
    def center(self) -> tuple[int, int]:
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)

    # Functin determines if one randomly generated rectangle will intersect with another in map
    # generation.
    def intersects(self, other: "Rect") -> bool:
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


# Generate dungeon calls our Rect class and provides a base grid and rooms to carve out of it.
def generate_dungeon() -> tuple[list[list[str]], list[Rect]]:
    rooms = []

    # Grid is a matrix of "#" that match our chosen "map" dimensions.
    grid = [["#" for x in range(MAP_WIDTH)] for y in range(MAP_HEIGHT)]

    # Attempt to create 25 rooms.
    for i in range(MAX_ROOM_ATTEMPTS):
        # Height and width are random values within a set range of dimensions.
        w = random.randint(MIN_ROOM_WIDTH, MAX_ROOM_WIDTH)
        h = random.randint(MIN_ROOM_HEIGHT, MAX_ROOM_HEIGHT)

        # x and y coordinates for our room must always fall between our "map" boundaries.
        x = random.randint(MAP_MARGIN, MAP_WIDTH - w - MAP_MARGIN)
        y = random.randint(MAP_MARGIN, MAP_HEIGHT - h - MAP_MARGIN)

        # Use the above dimensions to create a rectangle object.
        rec = Rect.from_dimensions(x, y, w, h)

        # Using Rect.intersects() to determine if a generated rectangle intersects with one that
        # already exists.
        collision = False
        for room in rooms:
            # If the rectangle will instersect we discard it and move on.
            if rec.intersects(room):
                collision = True
                break
        # If the rectangle will not collide with another we carve it out the grid and add it to the
        # rooms list.
        if not collision:
            for y in range(rec.y1, rec.y2):
                for x in range(rec.x1, rec.x2):
                    grid[y][x] = "."
            rooms.append(rec)

    # Loop that hits every room in rooms and "links itself" to the previous in the list.
    for i in range(1, len(rooms)):
        # Get coords for previous and current room
        prev_x, prev_y = rooms[i - 1].center
        new_x, new_y = rooms[i].center

        # Draw L corridor one of two ways to connect the two "linked rooms".
        # Corridors do intersect but the emergent chaos seems to work.
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

    # Return our grid (used as "mapping for game world generation") and rooms (a list of Rec that all
    # exist in the same map while not overlapping and remaining within boundaries).
    return grid, rooms
