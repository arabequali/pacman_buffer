import mazegenerator
import pygame
from typing import Any

from src.objects import Player, Pacgum, SuperPacgum
from src.assets import Asset

class Maze:

    def __init__(
        self,
        maze_w: int,
        maze_h: int,
        assets
    ) -> None:

        self.maze = mazegenerator.MazeGenerator((maze_w, maze_h)).maze
        self.assets = assets
        self.live_maze = self._create_live_maze()

    def get_maze(self) -> list[list[int]]:
        return (self.maze)

    def get_live_maze(self) -> list[list[list[int]]]:
        return (self.live_maze)

    def _create_live_maze(self) -> list[list[list[Any]]]:
        """
        The live maze will put every objects in the cell + the walls opened or close.
        0: nothing in cell
        1: pacgum in cell
        2: pacman in cell
        3: ghost in cell
        """

        pacgum_asset = self.assets.get_asset("pacgum.png")

        live_maze = []
        for line_number, line in enumerate(self.maze):
            live_maze.append([])
            for cell_number, cell in enumerate(line):
                if cell != 15:
                    live_maze[line_number].append([cell, Pacgum(cell_number, line_number, pacgum_asset, 10)])
                else:
                    live_maze[line_number].append([cell, 0])

        player = Player(len(live_maze) // 2, len(live_maze[0]) // 2, self.assets.get_asset("player.png"), -1)
        live_maze[player.x][player.y][1] = player
        return (live_maze)

    def is_pacgum(
        self,
        line: int,
        index: int,
    ) -> None:
        if (isinstance(self.live_maze[line][index][1], Pacgum) or isinstance(self.live_maze[line][index][1], SuperPacgum)):
            return (1)
        return (0)

    def search_player(self) -> tuple[int]:
        for line_index, line in enumerate(self.live_maze):
            for cell_index, cell in enumerate(line):
                if (isinstance(cell[1], Player)):
                    return (tuple([cell_index, line_index]))
        return (tuple([None, None]))

    def modify_cell_live_maze(
        self,
        line: int,
        index: int,
        new_object: Any
    ) -> None:
        self.live_maze[line][index][1] = new_object

    def display_score(
        self,
        surface: pygame.Surface,
        game
    ) -> None:

        score = str(game.score)

        score_asset = self.assets.get_asset("score.png")
        score_asset.resize_asset(surface.get_width() / 30, surface.get_height() / 30)

        zero_asset = self.assets.get_asset("zero.png")
        zero_asset.resize_asset(surface.get_width() / 30, surface.get_height() / 30)

        one_asset = self.assets.get_asset("one.png")
        one_asset.resize_asset(surface.get_width() / 30, surface.get_height() / 30)

        two_asset = self.assets.get_asset("two.png")
        two_asset.resize_asset(surface.get_width() / 30, surface.get_height() / 30)

        three_asset = self.assets.get_asset("three.png")
        three_asset.resize_asset(surface.get_width() / 30, surface.get_height() / 30)

        four_asset = self.assets.get_asset("four.png")
        four_asset.resize_asset(surface.get_width() / 30, surface.get_height() / 30)

        five_asset = self.assets.get_asset("five.png")
        five_asset.resize_asset(surface.get_width() / 30, surface.get_height() / 30)

        six_asset = self.assets.get_asset("six.png")
        six_asset.resize_asset(surface.get_width() / 30, surface.get_height() / 30)

        seven_asset = self.assets.get_asset("seven.png")
        seven_asset.resize_asset(surface.get_width() / 30, surface.get_height() / 30)

        eight_asset = self.assets.get_asset("eight.png")
        eight_asset.resize_asset(surface.get_width() / 30, surface.get_height() / 30)

        nine_asset = self.assets.get_asset("nine.png")
        nine_asset.resize_asset(surface.get_width() / 30, surface.get_height() / 30)

        surface.blit(score_asset.image, (0, 0))
        for i in range(len(score)):
            if score[i] == '0':
                surface.blit(zero_asset.image, ((surface.get_width() / 30) * (i + 1), 0))
            elif score[i] == '1':
                surface.blit(one_asset.image, ((surface.get_width() / 30) * (i + 1), 0))
            elif score[i] == '2':
                surface.blit(two_asset.image, ((surface.get_width() / 30) * (i + 1), 0))
            elif score[i] == '3':
                surface.blit(three_asset.image, ((surface.get_width() / 30) * (i + 1), 0))
            elif score[i] == '4':
                surface.blit(four_asset.image, ((surface.get_width() / 30) * (i + 1), 0))
            elif score[i] == '5':
                surface.blit(five_asset.image, ((surface.get_width() / 30) * (i + 1), 0))
            elif score[i] == '6':
                surface.blit(six_asset.image, ((surface.get_width() / 30) * (i + 1), 0))
            elif score[i] == '7':
                surface.blit(seven_asset.image, ((surface.get_width() / 30) * (i + 1), 0))
            elif score[i] == '8':
                surface.blit(eight_asset.image, ((surface.get_width() / 30) * (i + 1), 0))
            elif score[i] == '9':
                surface.blit(nine_asset.image, ((surface.get_width() / 30) * (i + 1), 0))

    def display_wall(
        self,
        surface: pygame.Surface,
        cell: int,
        live_pos: tuple[int],
        walls_size: tuple[int],
        walls_assets: tuple[pygame.Surface]
    ) -> None:

        x0 = live_pos[0]
        y0 = live_pos[1]

        wall_w = walls_size[0]
        wall_h = walls_size[1]

        x1 = x0 + wall_w
        y1 = y0 + wall_h

        hor_wall_image = walls_assets[0]
        ver_wall_image = walls_assets[1]

        if cell >= 8:
            surface.blit(ver_wall_image, (x0, y0))
            cell -= 8
        if cell >= 4:
            surface.blit(hor_wall_image, (x0, y1))
            cell -= 4
        if cell >= 2:
            surface.blit(ver_wall_image, (x1, y0))
            cell -= 2
        if cell >= 1:
            surface.blit(hor_wall_image, (x0, y0))
            cell -= 1

    def maze_pipeline(
        self,
        surface: pygame.Surface,
        window_w,
        window_h,
        padding_w,
        padding_h
    ) -> None:
        """Display the maze according to the live_maze"""

        wall_w = (window_w - padding_w * 2) / len(self.live_maze)
        wall_h = (window_h - padding_h * 2) / len(self.live_maze[0])

        player = self.assets.get_asset("player.png")
        player.resize_asset(wall_w / 1.5, wall_h / 1.5)

        horizontal_wall_image = self.assets.get_asset("horizontal_walls.png")
        horizontal_wall_image.resize_asset(wall_w, wall_h / 10)

        vertical_wall_image = self.assets.get_asset("vertical_walls.png")
        vertical_wall_image.resize_asset(wall_w / 10, wall_h)

        for line_index, line in enumerate(self.live_maze):

            for number_index, number in enumerate(line):

                cell = number[0]
                cell_info = number[1]

                x0 = padding_w + number_index * wall_w
                y0 = padding_h + line_index * wall_h

                self.display_wall(surface, cell, (x0, y0), (wall_w, wall_h), (horizontal_wall_image.image, vertical_wall_image.image))

                if cell_info != 0:
                    surface.blit(cell_info.asset.image, (x0 + player.image.get_width() / 2, y0 + player.image.get_height() / 2))
