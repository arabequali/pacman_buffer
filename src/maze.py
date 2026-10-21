import mazegenerator


class Maze:

    def __init__(
        self,
        maze_w: int,
        maze_h: int
    ) -> None:

        self.maze = mazegenerator.MazeGenerator((maze_w, maze_h)).maze
        self.live_maze = self._create_live_maze()

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

    def display_maze(self) -> None:
        return (None)
