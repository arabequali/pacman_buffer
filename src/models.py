"""Validated configuration model."""

from pydantic import BaseModel


class Config(BaseModel):
    """Game configuration (every field has a safe default)."""

    level_1_seed: int = 42
    level_1_size: list[int] = [29, 29]
    level_size_increase: int = 5
    level_max_size: int = 49
    level_count: int = 10
    level_max_time: int = 240

    lives: int = 3

    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 100
    points_per_ghosts: int = 500

    player_speed: float = 8.0
    ghost_speed: float = 6.5
    power_duration: float = 8.0
    ghost_respawn_time: float = 5.0

    cheat_mode: bool = False
    highscore_filename_path: str = "highscores.json"
