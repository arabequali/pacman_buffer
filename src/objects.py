"""Game objects: collectibles and moving entities (no graphics here)."""

import random
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.maze import Maze


class Direction(Enum):
    """The four directions: (dx, dy, wall bit of the maze encoding)."""

    UP = (0, -1, 1)
    RIGHT = (1, 0, 2)
    DOWN = (0, 1, 4)
    LEFT = (-1, 0, 8)

    @property
    def dx(self) -> int:
        """Horizontal step."""
        return int(self.value[0])

    @property
    def dy(self) -> int:
        """Vertical step."""
        return int(self.value[1])

    @property
    def wall_bit(self) -> int:
        """Bit of the cell value that is set when this side has a wall."""
        return int(self.value[2])

    @property
    def opposite(self) -> "Direction":
        """The reverse direction."""
        return Direction((-self.dx, -self.dy, {1: 4, 4: 1, 2: 8,
                                               8: 2}[self.wall_bit]))


class Objects:
    """Anything located in a maze cell."""

    def __init__(self, x: int, y: int) -> None:
        """Place the object on cell (x, y)."""
        self.x = x
        self.y = y


class Static(Objects):
    """A collectible worth some points."""

    def __init__(self, x: int, y: int, score_given: int) -> None:
        """Create a collectible giving `score_given` points."""
        super().__init__(x, y)
        self.score_given = score_given


class Pacgum(Static):
    """A small dot."""


class SuperPacgum(Pacgum):
    """A power pellet: makes the ghosts edible."""


class Moving(Objects):
    """An entity travelling from cell to cell at `speed` cells/second.

    `progress` (0..1) is how far it is between (x, y) and the next cell
    in `direction`; `direction` is None while the entity is standing.
    """

    def __init__(self, x: int, y: int, speed: float) -> None:
        """Create a standing entity on (x, y)."""
        super().__init__(x, y)
        self.start = (x, y)
        self.speed = speed
        self.direction: Direction | None = None
        self.facing = Direction.RIGHT
        self.progress = 0.0

    @property
    def fx(self) -> float:
        """Horizontal position in cells (fractional while moving)."""
        if self.direction is None:
            return float(self.x)
        return self.x + self.direction.dx * self.progress

    @property
    def fy(self) -> float:
        """Vertical position in cells (fractional while moving)."""
        if self.direction is None:
            return float(self.y)
        return self.y + self.direction.dy * self.progress

    def reset(self) -> None:
        """Go back to the starting cell and stand still."""
        self.x, self.y = self.start
        self.direction = None
        self.progress = 0.0

    def reverse(self) -> None:
        """Turn around immediately (also in the middle of a corridor)."""
        if self.direction is None:
            return
        if self.progress == 0.0:
            # exactly on a cell centre: only the heading changes
            self.direction = self.direction.opposite
            self.facing = self.direction
            return
        self.x += self.direction.dx
        self.y += self.direction.dy
        self.direction = self.direction.opposite
        self.facing = self.direction
        self.progress = 1.0 - self.progress

    def choose_direction(self, maze: "Maze",
                         current: Direction | None) -> Direction | None:
        """Pick the direction to take from the current cell centre."""
        raise NotImplementedError

    def arrived(self) -> None:
        """Hook called every time a new cell centre is reached."""

    def update(self, dt: float, maze: "Maze") -> None:
        """Advance the entity by `dt` seconds."""
        budget = self.speed * dt
        while budget > 1e-9:
            if self.direction is None:
                self.direction = self.choose_direction(maze, None)
                if self.direction is None:
                    return
                self.facing = self.direction
            remaining = 1.0 - self.progress
            if budget < remaining:
                self.progress += budget
                return
            budget -= remaining
            self.x += self.direction.dx
            self.y += self.direction.dy
            self.progress = 0.0
            self.arrived()
            self.direction = self.choose_direction(maze, self.direction)
            if self.direction is None:
                return
            self.facing = self.direction


class Player(Moving):
    """Pac-Man, driven by the keyboard."""

    def __init__(self, x: int, y: int, speed: float) -> None:
        """Create the player on its start cell."""
        super().__init__(x, y, speed)
        self.desired: Direction | None = None
        self.visited: list[tuple[int, int]] = []

    def set_desired(self, direction: Direction) -> None:
        """Remember the wanted direction; reversing is immediate."""
        self.desired = direction
        if (self.direction is not None
                and direction == self.direction.opposite):
            self.reverse()

    def reset(self) -> None:
        """Back to the start with no pending input."""
        super().reset()
        self.desired = None
        self.visited.clear()

    def arrived(self) -> None:
        """Record the cell so the game can eat what is there."""
        self.visited.append((self.x, self.y))

    def choose_direction(self, maze: "Maze",
                         current: Direction | None) -> Direction | None:
        """Take the wanted direction if free, else keep going, else stop."""
        if self.desired and maze.can_move(self.x, self.y, self.desired):
            return self.desired
        if current and maze.can_move(self.x, self.y, current):
            return current
        return None


GHOST_NAMES = ("blinky", "pinky", "inky", "clyde")


class Ghost(Moving):
    """A ghost. Each one has its own way of chasing the player.

    - blinky: runs straight at the player (shortest path).
    - pinky: ambushes, aiming 4 cells ahead of the player.
    - inky: unpredictable, half random half chasing.
    - clyde: chases from afar, goes back to its corner when close.
    """

    def __init__(self, name: str, corner: tuple[int, int], speed: float,
                 player: Player, rng: random.Random,
                 release_delay: float) -> None:
        """Create a ghost waiting in its corner."""
        super().__init__(corner[0], corner[1], speed)
        self.name = name
        self.base_speed = speed
        self.player = player
        self.rng = rng
        self.release_delay = release_delay
        self.wait = release_delay
        self.edible = False
        self.eaten = False
        self.respawn_timer = 0.0

    def reset(self) -> None:
        """Back to the corner, waiting to be released again."""
        super().reset()
        self.wait = self.release_delay
        self.edible = False
        self.eaten = False
        self.respawn_timer = 0.0

    @property
    def active(self) -> bool:
        """True when the ghost can hurt (or be hurt by) the player."""
        return not self.eaten

    def eat(self, respawn_time: float) -> None:
        """The player ate this ghost: it vanishes for a while."""
        self.eaten = True
        self.edible = False
        self.respawn_timer = respawn_time
        self.x, self.y = self.start
        self.direction = None
        self.progress = 0.0

    def set_edible(self, edible: bool) -> None:
        """Start or stop the frightened state."""
        if edible and not self.edible and self.active:
            self.reverse()
        self.edible = edible and self.active

    def _options(self, maze: "Maze",
                 current: Direction | None) -> list[Direction]:
        """Free directions, avoiding a U-turn unless it is the only way."""
        free = [d for d in Direction if maze.can_move(self.x, self.y, d)]
        if current is not None and len(free) > 1:
            free = [d for d in free if d != current.opposite]
        return free

    def _best(self, maze: "Maze", options: list[Direction],
              target: tuple[int, int], farthest: bool = False) -> Direction:
        """Option getting closest to (or farthest from) `target`."""
        field = maze.distance_field(*target)
        scored = []
        for d in options:
            value = field[self.y + d.dy][self.x + d.dx]
            scored.append((-value if farthest else value, d))
        best = min(score for score, _ in scored)
        return self.rng.choice([d for s, d in scored if s == best])

    def _ahead_of_player(self, maze: "Maze") -> tuple[int, int]:
        """Cell up to 4 steps in front of the player."""
        x, y = self.player.x, self.player.y
        d = self.player.facing
        for _ in range(4):
            if not maze.can_move(x, y, d):
                break
            x, y = x + d.dx, y + d.dy
        return x, y

    def choose_direction(self, maze: "Maze",
                         current: Direction | None) -> Direction | None:
        """Decide where to go at a junction."""
        options = self._options(maze, current)
        if not options:
            return None
        if len(options) == 1:
            return options[0]
        player_cell = (self.player.x, self.player.y)
        if self.edible:
            if self.rng.random() < 0.15:
                return self.rng.choice(options)
            return self._best(maze, options, player_cell, farthest=True)
        if self.name == "pinky":
            return self._best(maze, options, self._ahead_of_player(maze))
        if self.name == "inky" and self.rng.random() < 0.5:
            return self.rng.choice(options)
        if self.name == "clyde":
            distance = maze.distance_field(*player_cell)[self.y][self.x]
            if distance < 8:
                return self._best(maze, options, self.start)
        return self._best(maze, options, player_cell)
