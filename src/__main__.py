from os import listdir
from os.path import isfile, join
from pydantic import BaseModel, ValidationError
import json

from src.display import Display
from src.assets import Assets
from src.maze import Maze
from src.objects import Player
from src.game import Game
from src.menus import MainMenu
from src.models import Config


if __name__ == '__main__':

    with open("config.json", "r") as file:
        config_file = json.load(file)
        Config.model_validate(config_file)

    assets = [f for f in listdir("assets/") if isfile(join("assets/", f))]
    assets = Assets(assets)

    maze = Maze(config_file["level_1_size"][0], config_file["level_1_size"][1], assets)

    game = Game(maze, assets)
    menu = MainMenu(assets)

    Display(maze, assets, game, menu)
