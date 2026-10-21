from os import listdir
from os.path import isfile, join

from src.display import Display
from src.assets import Assets
from src.maze import Maze


if __name__ == '__main__':
    maze = Maze(15, 15)

    assets = [f for f in listdir("assets/") if isfile(join("assets/", f))]
    assets = Assets(assets)

    Display(maze, assets)
