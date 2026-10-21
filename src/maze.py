import mazegenerator
import pygame


class Maze:

    def __init__(
        self,
        maze_w: int,
        maze_h: int,
        assets
    ) -> None:

        self.maze = mazegenerator.MazeGenerator((maze_w, maze_h)).maze
        self.live_maze = self._create_live_maze()
        self.assets = assets

    def maze(self) -> list[list[int]]:
        return (self.maze)

    def live_maze(self) -> list[list[list[int]]]:
        return (self.live_maze)

    def _create_live_maze(self) -> list[list[list[int]]]:
        """The live maze will put every objects in the cell + the walls opened or close.
        1: pacgum in cell
        2: pacman in cell
        3: ghost in cell"""

        live_maze = []
        for line in self.maze:
            for cell in line:
                live_maze.append([cell, 0])
        return (live_maze)

    def display_maze(
        self,
        surface: pygame.Surface
    ) -> None:
        """Display the maze according to the live_maze"""

        window_w = surface.get_width()
        window_h = surface.get_height()

        border_size_width = window_w / 20
        border_size_height = window_h / 20

        width_wall = (window_w - border_size_width * 2) / len(self.maze)
        height_wall = (window_h - border_size_height * 2) / len(self.maze[0])

        horizontal_wall_image = self.assets.get_asset("horizontal_walls.png")
        vertical_wall_image = self.assets.get_asset("vertical_walls.png")
        for line_index, line in enumerate(self.maze):
            for number_index, number in enumerate(line):
                x0 = border_size_width + number_index * width_wall
                y0 = border_size_height + line_index * height_wall

                x1 = x0 + width_wall
                y1 = y0 + height_wall

                hor_wall_w = horizontal_wall_image.image.get_width()
                hor_wall_h = horizontal_wall_image.image.get_height()

                ver_wall_w = vertical_wall_image.image.get_width()
                ver_wall_h = vertical_wall_image.image.get_height()

                if number >= 8:
                    vertical_wall_image.resize_asset(10, height_wall)
                    surface.blit(vertical_wall_image.image, (x0, y0 + hor_wall_h / 2))
                    number -= 8
                if number >= 4:
                    horizontal_wall_image.resize_asset(width_wall, 10)
                    surface.blit(horizontal_wall_image.image, (x0 + ver_wall_w / 2, y1))
                    number -= 4
                if number >= 2:
                    vertical_wall_image.resize_asset(10, height_wall)
                    surface.blit(vertical_wall_image.image, (x1, y0 + hor_wall_h / 2))
                    number -= 2
                if number >= 1:
                    horizontal_wall_image.resize_asset(width_wall, 10)
                    surface.blit(horizontal_wall_image.image, (x0 + ver_wall_w / 2, y0))
                    number -= 1
