import pygame


class Display:

    def __init__(
        self,
        maze,
        assets
    ) -> None:
        pygame.init()
        self.maze = maze
        self.assets = assets
        self.pipeline()

    def pipeline(self) -> None:
        screen = pygame.display.set_mode((720, 720))

        running = True
        while (running):
            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    running = False

            self.maze.display_maze(screen)
            pygame.display.flip()
