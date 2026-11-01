from os import listdir
from os.path import isfile, join

from src.display import Display
from src.assets import Assets
from src.maze import Maze
from src.objects import Player
from src.game import Game
from src.menus import MainMenu


if __name__ == '__main__':
    assets = [f for f in listdir("assets/") if isfile(join("assets/", f))]
    assets = Assets(assets)

    maze = Maze(15, 15, assets)

    game = Game(maze, assets)
    menu = MainMenu(assets)

    Display(maze, assets, game, menu)
