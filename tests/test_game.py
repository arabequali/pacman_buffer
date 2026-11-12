"""Tests for the maze and the game rules."""

import random
from typing import Any

import pytest

from src.game import Game, GameState, build_level_spec
from src.maze import Maze, MazeError
from src.models import Config
from src.objects import Direction


def small_config(**kwargs: Any) -> Config:
    """A fast config with small mazes."""
    return Config(level_1_size=[15, 15], level_max_time=60, **kwargs)


def current(game: Game) -> GameState:
    """Current state (avoids static type narrowing in tests)."""
    return game.state


def test_maze_is_valid() -> None:
    """Start is playable and every corner is reachable."""
    maze = Maze.generate(29, 29, 42)
    assert maze.start in maze.playable
    assert all(c in maze.playable for c in maze.corners)


def test_seed_is_reproducible() -> None:
    """The fixed seed of level 1 gives the same maze."""
    assert (Maze.generate(21, 21, 42).grid
            == Maze.generate(21, 21, 42).grid)


def test_bad_grid_rejected() -> None:
    """Invalid grids raise MazeError."""
    with pytest.raises(MazeError):
        Maze([])
    with pytest.raises(MazeError):
        Maze([[99, 0], [0, 0]])
    with pytest.raises(MazeError):
        Maze.generate(-5, 3, 1)


def test_level_specs() -> None:
    """Sizes grow, seeds follow the rules, sizes are capped."""
    cfg = Config()
    first, third, last = (build_level_spec(cfg, n) for n in (1, 3, 10))
    assert first.seed == 42 and third.seed == 0
    assert (first.width, third.width) == (29, 39)
    assert last.width == cfg.level_max_size
    assert third.time_limit > first.time_limit


def test_initial_state() -> None:
    """4 ghosts in the corners, 4 super-pacgums, player at the centre."""
    game = Game(small_config(), rng=random.Random(1))
    corners = game.maze.corners
    assert [(g.x, g.y) for g in game.ghosts] == corners
    assert len(game.ghosts) == 4
    assert all(type(game.pellets[c]).__name__ == "SuperPacgum"
               for c in corners)
    assert (game.player.x, game.player.y) == game.maze.start
    assert game.lives == 3


def test_player_eats_and_scores() -> None:
    """Walking over a pacgum gives points."""
    game = Game(small_config(), rng=random.Random(1))
    for d in Direction:
        if game.maze.can_move(game.player.x, game.player.y, d):
            game.set_direction(d)
            break
    for _ in range(30):
        game.frozen = False
        game.update(1 / 60)
        game.invincible = True
    assert game.score > 0
    assert game.score % 10 == 0


def test_ghost_collision_and_game_over() -> None:
    """A ghost touching the player removes lives until game over."""
    game = Game(small_config(lives=1), rng=random.Random(1))
    ghost = game.ghosts[0]
    ghost.x, ghost.y = game.player.x, game.player.y
    ghost.wait = 0
    game.update(1 / 60)
    assert current(game) == GameState.PAUSE_AFTER_HIT
    assert game.lives == 0
    game.update(5)
    assert current(game) == GameState.GAME_OVER


def test_edible_ghost_is_eaten() -> None:
    """Power mode: touching a ghost gives points and hides it."""
    game = Game(small_config(), rng=random.Random(1))
    game.cheat_enabled = True
    game.cheat_power()
    ghost = game.ghosts[0]
    ghost.x, ghost.y = game.player.x, game.player.y
    before = game.score
    game.update(1 / 60)
    assert game.score == before + game.config.points_per_ghosts
    assert ghost.eaten and game.lives == 3
    game.update(game.config.ghost_respawn_time + 1)
    assert not ghost.eaten


def test_cheats_need_cheat_mode() -> None:
    """Cheat methods do nothing when cheat mode is off."""
    game = Game(small_config(), rng=random.Random(1))
    game.cheat_add_life()
    game.cheat_skip_level()
    assert game.lives == 3 and game.level == 1
    game.cheat_enabled = True
    game.cheat_add_life()
    assert game.lives == 4


def test_skip_all_levels_to_victory() -> None:
    """Skipping every level ends in victory and keeps score/lives."""
    game = Game(small_config(level_count=3), cheat=True,
                rng=random.Random(2))
    for expected in (1, 2, 3):
        assert game.level == expected
        game.cheat_skip_level()
        game.update(3)
    assert game.state == GameState.VICTORY
    assert game.lives == 3


def test_time_out_costs_a_life() -> None:
    """When the clock reaches 0 a life is lost and the clock restarts."""
    game = Game(small_config(), cheat=True, rng=random.Random(3))
    game.invincible = True
    game.cheat_low_time()
    for _ in range(400):
        game.update(1 / 30)
        if game.state != GameState.PLAYING:
            break
    assert game.lives == 2
    assert game.message == "Time's up!"
    game.update(3)
    assert game.state == GameState.PLAYING
    assert game.time_left > 5


def test_player_cannot_cross_walls() -> None:
    """Moving randomly never puts the player on a closed cell."""
    game = Game(small_config(), cheat=True, rng=random.Random(4))
    game.invincible = True
    rng = random.Random(5)
    for i in range(1500):
        if i % 15 == 0:
            game.set_direction(rng.choice(list(Direction)))
        game.update(1 / 60)
        assert (game.player.x, game.player.y) in game.maze.playable
        for ghost in game.ghosts:
            assert (ghost.x, ghost.y) in game.maze.playable
