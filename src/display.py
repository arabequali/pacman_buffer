import pygame
import time


class Display:
    """
    The display class.
    Usage: Display()
    Arguments:
    - maze: Maze class
    - assets: Assets class (which contains every assets in a list)

    When the class is created, it executes the pipeline which display the window used to play the game.
    """

    def __init__(
        self,
        maze,
        assets,
        game
    ) -> None:
        pygame.init()
        self.window_w = 720
        self.window_h = 720

        self.padding_w = self.window_w / 20
        self.padding_h = self.window_h / 20

        self.maze = maze
        self.assets = assets
        self.game = game
        self.pipeline()

    def pipeline(self) -> None:
        screen = pygame.display.set_mode((self.window_w, self.window_h))
        clock = pygame.time.Clock()
        ticking = 0

        running = True
        while (running):
            screen.fill('dark blue')

            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    running = False

            key_pressed = pygame.key.get_pressed()
            if ticking % 10 == 0:
                self.game.action_pipeline(key_pressed)
            self.maze.maze_pipeline(screen, self.window_w, self.window_h, self.padding_w, self.padding_h)
            self.maze.display_score(screen, self.game)

            pygame.display.flip()
            clock.tick(60)
            ticking += 1
