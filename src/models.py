from pydantic import BaseModel


class Config(BaseModel):
    maze_size: tuple[int]
