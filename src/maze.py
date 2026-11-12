"""Maze built on top of the assigned `mazegenerator` package."""

import logging
from collections import deque
from typing import Any

from src.objects import Direction

log = logging.getLogger("pacman.maze")

CLOSED = 15  # fully walled cell (the '42' pattern of the generator)


class MazeError(Exception):
    """Raised when a maze cannot be generated or is unusable."""


class Maze:
    """A grid of cells; each int holds the walls of that cell.

    Bits: 1 = north, 2 = east, 4 = south, 8 = west wall.
    Coordinates are (x, y) = (column, row).
    """

    def __init__(self, grid: list[list[int]]) -> None:
        """Validate the grid and precompute the playable area."""
        if (not grid or not grid[0]
                or any(len(row) != len(grid[0]) for row in grid)):
            raise MazeError("maze grid is empty or not rectangular")
        if any(not isinstance(c, int) or isinstance(c, bool)
               or not 0 <= c <= 15 for row in grid for c in row):
            raise MazeError("maze grid contains invalid cell values")
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0])
        self._fields: dict[tuple[int, int], list[list[int]]] = {}
        self.corners = [(0, 0), (self.width - 1, 0),
                        (0, self.height - 1),
                        (self.width - 1, self.height - 1)]
        self.playable = self._flood(self.corners[0])
        for corner in self.corners:
            if corner not in self.playable:
                raise MazeError("generated maze is not connected")
        self.start = self._find_start()

    @classmethod
    def generate(cls, width: int, height: int, seed: int = 0) -> "Maze":
        """Generate a maze with the assigned package (seed 0 = random).

        PERFECT is False so the maze has loops and no dead ends.
        """
        try:
            import mazegenerator
            generator = mazegenerator.MazeGenerator(
                (width, height), perfect=False, seed=seed)
            grid: Any = generator.maze
            return cls([list(row) for row in grid])
        except MazeError:
            raise
        except Exception as exc:
            raise MazeError(f"maze generator failed: {exc}") from exc

    def cell(self, x: int, y: int) -> int:
        """Wall bits of cell (x, y)."""
        return self.grid[y][x]

    def can_move(self, x: int, y: int, direction: Direction) -> bool:
        """True if one can walk from (x, y) towards `direction`."""
        nx, ny = x + direction.dx, y + direction.dy
        if not (0 <= nx < self.width and 0 <= ny < self.height):
            return False
        if self.grid[y][x] & direction.wall_bit:
            return False
        return self.grid[ny][nx] != CLOSED

    def _flood(self, origin: tuple[int, int]) -> set[tuple[int, int]]:
        """All cells reachable from `origin`."""
        seen = {origin}
        queue = deque([origin])
        while queue:
            x, y = queue.popleft()
            for d in Direction:
                if self.can_move(x, y, d):
                    nxt = (x + d.dx, y + d.dy)
                    if nxt not in seen:
                        seen.add(nxt)
                        queue.append(nxt)
        return seen

    def _find_start(self) -> tuple[int, int]:
        """Playable cell closest to the centre of the maze."""
        cx, cy = (self.width - 1) / 2, (self.height - 1) / 2
        return min(self.playable, key=lambda c: (
            (c[0] - cx) ** 2 + (c[1] - cy) ** 2, c[1], c[0]))

    def distance_field(self, x: int, y: int) -> list[list[int]]:
        """Walking distance from (x, y) to every cell (-1 if unreachable).

        Results are cached because ghosts ask for the same field often.
        """
        key = (x, y)
        if key in self._fields:
            return self._fields[key]
        field = [[-1] * self.width for _ in range(self.height)]
        field[y][x] = 0
        queue = deque([key])
        while queue:
            cx, cy = queue.popleft()
            for d in Direction:
                if self.can_move(cx, cy, d):
                    nx, ny = cx + d.dx, cy + d.dy
                    if field[ny][nx] < 0:
                        field[ny][nx] = field[cy][cx] + 1
                        queue.append((nx, ny))
        if len(self._fields) > 64:
            self._fields.clear()
        self._fields[key] = field
        return field
