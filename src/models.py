from pydantic import BaseModel


class Config(BaseModel):
    level_1_seed: int
    level_1_size: list[int]
    level_size_increase: int

    lives: int

    points_per_pacgum: int
    points_per_super_pacgum: int
    points_per_ghosts: int

    highscore_filename_path: str
