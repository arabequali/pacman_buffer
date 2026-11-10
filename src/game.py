import pygame
from typing import Sequence

from src.maze import Maze
from src.assets import Assets
from src.objects import Player


class Game:

    def __init__(
        self,
        maze: Maze,
        assets: Assets
    ) -> None:
        self.score = 0
        self.maze = maze

    def can_left(self, line: int, index: int) -> int:
        if self.maze.live_maze[line][index][0] < 8:
            return (1)
        return (0)

    def can_down(self, line: int, index: int) -> int:
        buffer = self.maze.live_maze[line][index][0]
        if buffer >= 8:
            buffer -= 8
        if buffer < 4:
            return (1)
        return (0)

    def can_right(self, line: int, index: int) -> int:
        buffer = self.maze.live_maze[line][index][0]
        if buffer >= 8:
            buffer -= 8
        if buffer >= 4:
            buffer -= 4
        if buffer < 2:
            return (1)
        return (0)

    def can_up(self, line: int, index: int) -> int:
        buffer = self.maze.live_maze[line][index][0]
        if buffer % 2 == 0:
            return (1)
        return (0)

    def go_left(
        self,
        player: Player,
        line: int,
        cell: int
    ) -> None:
        self.maze.modify_cell_live_maze(line, cell, 0)
        if self.maze.is_pacgum(line, cell - 1):
            self.score += self.maze.live_maze[line][cell - 1][1].score_given
        self.maze.modify_cell_live_maze(line, cell - 1, player)

    def go_down(
        self,
        player: Player,
        line: int,
        index: int
    ) -> None:
        self.maze.modify_cell_live_maze(line, index, 0)
        if self.maze.is_pacgum(line + 1, index):
            self.score += self.maze.live_maze[line + 1][index][1].score_given
        self.maze.modify_cell_live_maze(line + 1, index, player)

    def go_right(
        self,
        player: Player,
        line: int,
        index: int
    ) -> None:
        self.maze.modify_cell_live_maze(line, index, 0)
        if self.maze.is_pacgum(line, index + 1):
            self.score += self.maze.live_maze[line][index + 1][1].score_given
        self.maze.modify_cell_live_maze(line, index + 1, player)

    def go_up(
        self,
        player: Player,
        line: int,
        index: int
    ) -> None:
        self.maze.modify_cell_live_maze(line, index, 0)
        if self.maze.is_pacgum(line - 1, index):
            self.score += self.maze.live_maze[line - 1][index][1].score_given
        self.maze.modify_cell_live_maze(line - 1, index, player)

    def action_pipeline(
        self,
        key_pressed: Sequence[bool],
        ticking: int
    ) -> None:

        values = self.maze.search_player()
        if values[0] is not None and values[1] is not None:
            line_index = values[1]
            cell_index = values[0]
            player = self.maze.get_live_maze()[line_index][cell_index][1]

        if key_pressed[pygame.K_LEFT]:
            player.set_direction(3)
        elif key_pressed[pygame.K_DOWN] and self.can_down(line_index, cell_index):
            player.set_direction(2)
        elif key_pressed[pygame.K_RIGHT] and self.can_right(line_index, cell_index):
            player.set_direction(1)
        elif key_pressed[pygame.K_UP] and self.can_up(line_index, cell_index):
            player.set_direction(0)

        if ticking % 10 == 0:
            if player.get_direction() == 3 and self.can_left(line_index, cell_index):
                self.go_left(player, line_index, cell_index)
            elif player.get_direction() == 2 and self.can_down(line_index, cell_index):
                self.go_down(player, line_index, cell_index)
            elif player.get_direction() == 1 and self.can_right(line_index, cell_index):
                self.go_right(player, line_index, cell_index)
            elif player.get_direction() == 0 and self.can_up(line_index, cell_index):
                self.go_up(player, line_index, cell_index)
