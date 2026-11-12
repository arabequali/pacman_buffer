"""Game rules: levels, score, lives, timers, ghosts and cheats.

This module knows nothing about graphics so it can be unit-tested.
"""

import logging
import random
from dataclasses import dataclass
from enum import Enum

from src.maze import Maze, MazeError
from src.models import Config
from src.objects import (GHOST_NAMES, Direction, Ghost, Pacgum, Player,
                         SuperPacgum)

log = logging.getLogger("pacman.game")

HIT_DISTANCE = 0.7
DEATH_PAUSE = 1.6
LEVEL_PAUSE = 2.0
MAX_GENERATION_TRIES = 3


class GameState(Enum):
    """High level state of a run."""

    PLAYING = 1
    PAUSE_AFTER_HIT = 2
    LEVEL_DONE = 3
    GAME_OVER = 4
    VICTORY = 5


@dataclass
class LevelSpec:
    """Size, seed and time limit of one level."""

    number: int
    width: int
    height: int
    seed: int
    time_limit: float


def build_level_spec(config: Config, number: int) -> LevelSpec:
    """Compute the parameters of level `number` (1-based).

    Level 1 uses the fixed seed, the others are random (seed 0). The size
    grows with the level up to `level_max_size`, and the time limit grows
    with the maze area (level_max_time is the time of level 1).
    """
    base_w, base_h = config.level_1_size
    grow = config.level_size_increase * (number - 1)
    cap = config.level_max_size
    width = max(base_w, min(base_w + grow, cap))
    height = max(base_h, min(base_h + grow, cap))
    area_ratio = (width * height) / (base_w * base_h)
    return LevelSpec(
        number, width, height,
        config.level_1_seed if number == 1 else 0,
        config.level_max_time * area_ratio)


class Game:
    """One run of the game, from level 1 to victory or game over."""

    def __init__(self, config: Config, cheat: bool = False,
                 rng: random.Random | None = None) -> None:
        """Start a new run on level 1 (may raise MazeError)."""
        self.config = config
        self.cheat_enabled = cheat
        self.rng = rng or random.Random()
        self.score = 0
        self.lives = config.lives
        self.level = 0
        self.state = GameState.PLAYING
        self.message = ""
        self.error = ""
        self.invincible = False
        self.frozen = False
        self.speed_boost = False
        self.power_timer = 0.0
        self.state_timer = 0.0
        self.time_left = 0.0
        self.time_limit = 0.0
        self.pellets: dict[tuple[int, int], Pacgum] = {}
        self.maze: Maze
        self.player: Player
        self.ghosts: list[Ghost] = []
        self._start_level(1, strict=True)

    # ----------------------------------------------------------- levels
    def _start_level(self, number: int, strict: bool = False) -> bool:
        """Build level `number`. Returns False if generation failed."""
        spec = build_level_spec(self.config, number)
        maze: Maze | None = None
        for attempt in range(MAX_GENERATION_TRIES):
            try:
                seed = spec.seed if attempt == 0 else 0
                maze = Maze.generate(spec.width, spec.height, seed)
                break
            except MazeError as exc:
                log.error("level %d, attempt %d: %s",
                          number, attempt + 1, exc)
                self.error = str(exc)
        if maze is None:
            if strict:
                raise MazeError(self.error)
            return False
        self.error = ""
        self.maze = maze
        self.level = number
        self.time_limit = spec.time_limit
        self.time_left = spec.time_limit
        self.power_timer = 0.0
        self._populate()
        self.state = GameState.PLAYING
        self.message = ""
        return True

    def _populate(self) -> None:
        """Place pacgums, super-pacgums, the player and the ghosts."""
        cfg = self.config
        self.pellets = {}
        for (x, y) in self.maze.playable:
            self.pellets[(x, y)] = Pacgum(x, y, cfg.points_per_pacgum)
        for (x, y) in self.maze.corners:
            self.pellets[(x, y)] = SuperPacgum(
                x, y, cfg.points_per_super_pacgum)
        sx, sy = self.maze.start
        self.pellets.pop((sx, sy), None)
        self.player = Player(sx, sy, cfg.player_speed)
        level_factor = min(1.0 + 0.04 * (self.level - 1), 1.4)
        speed = cfg.ghost_speed * level_factor
        self.ghosts = [
            Ghost(name, corner, speed, self.player, self.rng, 2.0 * i)
            for i, (name, corner) in enumerate(
                zip(GHOST_NAMES, self.maze.corners))]

    @property
    def pellets_left(self) -> int:
        """Number of pacgums (small and super) still on the maze."""
        return len(self.pellets)

    @property
    def powered(self) -> bool:
        """True while the ghosts are edible."""
        return self.power_timer > 0

    def _reset_positions(self) -> None:
        """Player back to the centre, ghosts back to their corners."""
        self.player.reset()
        for ghost in self.ghosts:
            ghost.reset()
        self.power_timer = 0.0

    # ------------------------------------------------------------ input
    def set_direction(self, direction: Direction) -> None:
        """Player input."""
        if self.state == GameState.PLAYING:
            self.player.set_desired(direction)

    # ----------------------------------------------------------- update
    def update(self, dt: float) -> None:
        """Advance the game by `dt` seconds."""
        if self.state == GameState.PLAYING:
            self._update_playing(dt)
        elif self.state == GameState.PAUSE_AFTER_HIT:
            self.state_timer -= dt
            if self.state_timer <= 0:
                if self.lives <= 0:
                    self.state = GameState.GAME_OVER
                    self.message = "Game over"
                else:
                    self._reset_positions()
                    self.state = GameState.PLAYING
                    self.message = ""
        elif self.state == GameState.LEVEL_DONE:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self._next_level()

    def _next_level(self) -> None:
        """Move to the next level or win the game."""
        if self.level >= self.config.level_count:
            self.state = GameState.VICTORY
            self.message = "Victory"
        elif not self._start_level(self.level + 1):
            log.error("cannot build next level, ending the game")
            self.state = GameState.GAME_OVER
            self.message = "Level generation failed"

    def _update_playing(self, dt: float) -> None:
        """Run one step of the action."""
        self.time_left -= dt
        if self.time_left <= 0:
            self._time_out()
            return
        if self.power_timer > 0:
            self.power_timer -= dt
            if self.power_timer <= 0:
                self.power_timer = 0.0
                for ghost in self.ghosts:
                    ghost.set_edible(False)
        factor = 1.6 if self.speed_boost else 1.0
        self.player.speed = self.config.player_speed * factor
        self.player.update(dt, self.maze)
        self._eat_pellets()
        if self.pellets_left == 0:
            self._complete_level()
            return
        self._update_ghosts(dt)
        self._check_collisions()

    def _eat_pellets(self) -> None:
        """Eat what the player walked over since the last update."""
        for cell in self.player.visited:
            pellet = self.pellets.pop(cell, None)
            if pellet is None:
                continue
            self.score += pellet.score_given
            if isinstance(pellet, SuperPacgum):
                self._start_power()
        self.player.visited.clear()

    def _start_power(self) -> None:
        """Super-pacgum eaten: ghosts become edible for a while."""
        self.power_timer = self.config.power_duration
        for ghost in self.ghosts:
            ghost.set_edible(True)

    def _update_ghosts(self, dt: float) -> None:
        """Move the ghosts, handle release and respawn timers."""
        for ghost in self.ghosts:
            if ghost.eaten:
                ghost.respawn_timer -= dt
                if ghost.respawn_timer <= 0:
                    ghost.eaten = False
                    ghost.wait = 0.0
                continue
            if self.frozen:
                continue
            if ghost.wait > 0:
                ghost.wait -= dt
                continue
            ghost.speed = (ghost.base_speed * 0.6 if ghost.edible
                           else ghost.base_speed)
            ghost.update(dt, self.maze)

    def _check_collisions(self) -> None:
        """Ghost touches player: eat it (edible) or lose a life."""
        for ghost in self.ghosts:
            if not ghost.active:
                continue
            dist = ((ghost.fx - self.player.fx) ** 2
                    + (ghost.fy - self.player.fy) ** 2) ** 0.5
            if dist >= HIT_DISTANCE:
                continue
            if ghost.edible:
                self.score += self.config.points_per_ghosts
                ghost.eat(self.config.ghost_respawn_time)
            elif not self.invincible:
                self._lose_life("Caught!")
                return

    def _lose_life(self, message: str) -> None:
        """Remove a life and pause before resuming or ending."""
        self.lives -= 1
        self.state = GameState.PAUSE_AFTER_HIT
        self.state_timer = DEATH_PAUSE
        self.message = message

    def _time_out(self) -> None:
        """Time limit reached: lose a life and restart the level clock.

        The pacgums already eaten stay eaten (no score farming).
        """
        self.time_left = self.time_limit
        self._lose_life("Time's up!")

    def _complete_level(self) -> None:
        """All pacgums eaten."""
        self.state = GameState.LEVEL_DONE
        self.state_timer = LEVEL_PAUSE
        self.message = f"Level {self.level} complete!"

    # ------------------------------------------------------------ cheats
    def cheat_skip_level(self) -> None:
        """Win the current level immediately."""
        if self.cheat_enabled and self.state == GameState.PLAYING:
            self.pellets.clear()
            self._complete_level()

    def cheat_add_life(self) -> None:
        """Give one more life."""
        if self.cheat_enabled and self.state == GameState.PLAYING:
            self.lives += 1

    def cheat_toggle_invincible(self) -> None:
        """Ghosts cannot hurt the player."""
        if self.cheat_enabled:
            self.invincible = not self.invincible

    def cheat_toggle_freeze(self) -> None:
        """Ghosts stop moving."""
        if self.cheat_enabled:
            self.frozen = not self.frozen

    def cheat_toggle_speed(self) -> None:
        """Player moves faster."""
        if self.cheat_enabled:
            self.speed_boost = not self.speed_boost

    def cheat_power(self) -> None:
        """Make the ghosts edible, as if a super-pacgum was eaten."""
        if self.cheat_enabled and self.state == GameState.PLAYING:
            self._start_power()

    def cheat_low_time(self) -> None:
        """Leave only 5 seconds to test the time-out."""
        if self.cheat_enabled and self.state == GameState.PLAYING:
            self.time_left = min(self.time_left, 5.0)
