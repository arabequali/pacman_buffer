"""Everything that draws on the screen."""

import pygame

from src.assets import Assets
from src.game import Game, GameState
from src.highscores import ScoreEntry
from src.maze import Maze
from src.menus import MainMenu, PauseMenu
from src.objects import SuperPacgum

WIDTH = 800
HEIGHT = 900
HUD_HEIGHT = 80
MARGIN = 20

YELLOW = (255, 220, 0)
WHITE = (240, 240, 240)
RED = (255, 80, 80)
GREY = (150, 150, 150)
BG = (10, 10, 40)
GHOST_SPRITES = {
    "blinky": "ghost_red.png", "pinky": "ghost_pink.png",
    "inky": "ghost_cyan.png", "clyde": "ghost_orange.png",
}
ROTATION = {"RIGHT": 0, "UP": 90, "LEFT": 180, "DOWN": 270}
CHEAT_HELP = ("I invincible  N next level  G freeze ghosts  L +1 life  "
              "V speed  E edible ghosts  T low time")


class Display:
    """Window, fonts and drawing of every screen."""

    def __init__(self, assets: Assets) -> None:
        """Open the window (pygame must already be initialised)."""
        self.assets = assets
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pac-Man")
        self._fonts: dict[int, pygame.font.Font] = {}
        self._level_key: int | None = None
        self.cell = 10
        self.origin = (0, 0)
        self.wall_layer = pygame.Surface((1, 1))
        self.wall_origin = (0, 0)

    # ------------------------------------------------------------ text
    def font(self, size: int) -> pygame.font.Font:
        """Default font at the given size (cached)."""
        if size not in self._fonts:
            self._fonts[size] = pygame.font.Font(None, size)
        return self._fonts[size]

    def text(self, content: str, size: int, color: tuple[int, int, int],
             center: tuple[int, int] | None = None,
             topleft: tuple[int, int] | None = None,
             topright: tuple[int, int] | None = None) -> None:
        """Draw a line of text."""
        surface = self.font(size).render(content, True, color)
        rect = surface.get_rect()
        if center is not None:
            rect.center = center
        elif topleft is not None:
            rect.topleft = topleft
        elif topright is not None:
            rect.topright = topright
        self.screen.blit(surface, rect)

    def dim(self, alpha: int = 170) -> None:
        """Darken the whole screen (behind overlays)."""
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 0, 0, alpha))
        self.screen.blit(shade, (0, 0))

    def flip(self) -> None:
        """Show the frame."""
        pygame.display.flip()

    # ------------------------------------------------------------ menus
    def draw_main_menu(self, menu: MainMenu, scores: list[ScoreEntry],
                       cheat: bool, notice: str, now: int) -> None:
        """Main menu with image buttons and the best scores."""
        self.screen.fill(BG)
        self.text("PAC-MAN", 130, YELLOW, center=(WIDTH // 2, 80))
        size = (270, 90)
        for i, choice in enumerate(menu.entries):
            name = f"{choice}_button"
            selected = i == menu.cursor
            asset = self.assets.get_asset(
                name + ("_cursor.png" if selected else ".png"))
            image = asset.scaled(*size)
            y = 170 + i * 105
            x = (WIDTH - size[0]) // 2
            self.screen.blit(image, (x, y))
            if selected:
                self.text(">", 70, YELLOW, center=(x - 40, y + size[1] // 2))
        if notice:
            self.text(notice, 30, RED, center=(WIDTH // 2, 610))
        self.text("Best scores", 36, YELLOW, center=(WIDTH // 2, 660))
        for i, entry in enumerate(scores[:3]):
            self.text(f"{i + 1}. {entry.name} - {entry.score} pts", 32,
                      WHITE, center=(WIDTH // 2, 700 + i * 34))
        if not scores:
            self.text("No score yet", 30, GREY, center=(WIDTH // 2, 700))
        state = "ON" if cheat else "OFF"
        self.text(f"Cheat mode: {state} (press C to toggle)", 26,
                  YELLOW if cheat else GREY, center=(WIDTH // 2, 870))

    def draw_highscores(self, scores: list[ScoreEntry]) -> None:
        """Full top-10 table."""
        self.screen.fill(BG)
        self.text("HIGHSCORES", 100, YELLOW, center=(WIDTH // 2, 90))
        if not scores:
            self.text("No score yet", 44, GREY, center=(WIDTH // 2, 300))
        for i, entry in enumerate(scores):
            self.text(f"{i + 1}. {entry.name} - {entry.score} pts", 48,
                      WHITE, center=(WIDTH // 2, 190 + i * 55))
        self.text("Press ENTER or ESC to go back", 30, GREY,
                  center=(WIDTH // 2, 830))

    def draw_instructions(self, lines: list[str]) -> None:
        """Controls and rules."""
        self.screen.fill(BG)
        self.text("INSTRUCTIONS", 90, YELLOW, center=(WIDTH // 2, 70))
        y = 150
        for line in lines:
            if line.startswith("#"):
                y += 10
                self.text(line[1:], 40, YELLOW, topleft=(60, y))
            else:
                self.text(line, 30, WHITE, topleft=(80, y))
            y += 36
        self.text("Press ENTER or ESC to go back", 30, GREY,
                  center=(WIDTH // 2, 860))

    # ------------------------------------------------------------- game
    def prepare_level(self, maze: Maze) -> None:
        """Compute the layout and pre-draw the (static) walls."""
        avail_w = WIDTH - 2 * MARGIN
        avail_h = HEIGHT - HUD_HEIGHT - MARGIN
        self.cell = max(4, min(avail_w // maze.width,
                               avail_h // maze.height))
        cs = self.cell
        ox = (WIDTH - cs * maze.width) // 2
        oy = HUD_HEIGHT + (avail_h - cs * maze.height) // 2
        self.origin = (ox, oy)
        t = max(2, cs // 8)
        h_wall = self.assets.get_asset("horizontal_walls.png").trimmed()
        v_wall = self.assets.get_asset("vertical_walls.png").trimmed()
        h_img = h_wall.scaled(cs + t, t)
        v_img = v_wall.scaled(t, cs + t)
        layer = pygame.Surface((cs * maze.width + t, cs * maze.height + t),
                               pygame.SRCALPHA)
        g = maze.grid
        for y in range(maze.height):
            for x in range(maze.width):
                c = g[y][x]
                px, py = x * cs, y * cs
                if c & 1:
                    layer.blit(h_img, (px, py))
                if c & 8:
                    layer.blit(v_img, (px, py))
                if c & 4 and (y == maze.height - 1 or not g[y + 1][x] & 1):
                    layer.blit(h_img, (px, py + cs))
                if c & 2 and (x == maze.width - 1 or not g[y][x + 1] & 8):
                    layer.blit(v_img, (px + cs, py))
        self.wall_layer = layer
        self.wall_origin = (ox - t // 2, oy - t // 2)

    def _sprite(self, name: str, size: int, angle: int = 0) -> pygame.Surface:
        """Scaled (and rotated) game sprite."""
        return self.assets.get_asset(name).scaled(size, size, angle)

    def _blit_centered(self, image: pygame.Surface, fx: float,
                       fy: float) -> None:
        """Draw `image` centred on the cell position (fx, fy)."""
        cs = self.cell
        x = self.origin[0] + (fx + 0.5) * cs - image.get_width() / 2
        y = self.origin[1] + (fy + 0.5) * cs - image.get_height() / 2
        self.screen.blit(image, (round(x), round(y)))

    def draw_game(self, game: Game, now: int, cheat_help: bool) -> None:
        """Maze, pacgums, ghosts, player, HUD and state banners."""
        key = id(game.maze)
        if key != self._level_key:
            self.prepare_level(game.maze)
            self._level_key = key
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.wall_layer, self.wall_origin)
        cs = self.cell
        small = self._sprite("pacgum.png", max(2, cs // 4))
        big = self._sprite("super_pacgum.png", max(4, int(cs * 0.7)))
        blink_on = (now // 250) % 2 == 0
        for (x, y), pellet in game.pellets.items():
            if isinstance(pellet, SuperPacgum):
                if blink_on:
                    self._blit_centered(big, x, y)
            else:
                self._blit_centered(small, x, y)
        size = max(4, int(cs * 0.9))
        for ghost in game.ghosts:
            if not ghost.active:
                continue
            name = GHOST_SPRITES[ghost.name]
            if ghost.edible:
                ending = game.power_timer < 2.0 and (now // 150) % 2 == 0
                if not ending:
                    name = "ghost_scared.png"
            self._blit_centered(self._sprite(name, size), ghost.fx,
                                ghost.fy)
        angle = ROTATION[game.player.facing.name]
        self._blit_centered(self._sprite("player.png", size, angle),
                            game.player.fx, game.player.fy)
        self._draw_hud(game, cheat_help)
        if game.message and game.state != GameState.PLAYING:
            self._banner(game.message)

    def _banner(self, message: str) -> None:
        """Centered message over the maze."""
        band = pygame.Surface((WIDTH, 90), pygame.SRCALPHA)
        band.fill((0, 0, 0, 190))
        self.screen.blit(band, (0, HEIGHT // 2 - 45))
        self.text(message, 70, YELLOW, center=(WIDTH // 2, HEIGHT // 2))

    def _draw_hud(self, game: Game, cheat_help: bool) -> None:
        """Score, lives, level and remaining time (always visible)."""
        self.screen.fill(BG, (0, 0, WIDTH, HUD_HEIGHT))
        icon = self.assets.get_asset("score.png").scaled(34, 34)
        self.screen.blit(icon, (MARGIN, 10))
        self.text(f"{game.score}", 40, WHITE, topleft=(MARGIN + 42, 14))
        self.text(f"Level {game.level}/{game.config.level_count}", 40,
                  YELLOW, center=(WIDTH // 2 - 60, 28))
        life = self.assets.get_asset("player.png").scaled(30, 30)
        if game.lives <= 5:
            for i in range(max(0, game.lives)):
                self.screen.blit(life, (WIDTH // 2 + 80 + i * 34, 12))
        else:
            self.screen.blit(life, (WIDTH // 2 + 80, 12))
            self.text(f"x{game.lives}", 36, WHITE,
                      topleft=(WIDTH // 2 + 118, 16))
        seconds = max(0, int(game.time_left + 0.99))
        color = RED if seconds <= 10 else WHITE
        self.text(f"Time {seconds}", 40, color,
                  topright=(WIDTH - MARGIN, 14))
        if game.cheat_enabled:
            flags = (f"[{'x' if game.invincible else ' '}] I  "
                     f"[{'x' if game.frozen else ' '}] G  "
                     f"[{'x' if game.speed_boost else ' '}] V")
            self.text("CHEAT MODE  " + flags, 24, YELLOW,
                      topleft=(MARGIN, 52))
            if cheat_help:
                self.text(CHEAT_HELP, 20, GREY, topleft=(MARGIN + 260, 56))

    def draw_pause(self, menu: PauseMenu) -> None:
        """Pause overlay on top of the frozen game."""
        self.dim()
        self.text("PAUSED", 110, YELLOW, center=(WIDTH // 2, 300))
        for i, entry in enumerate(menu.entries):
            selected = i == menu.cursor
            label = ("> " if selected else "  ") + menu.LABELS[entry]
            self.text(label, 54, YELLOW if selected else WHITE,
                      center=(WIDTH // 2, 430 + i * 70))

    def draw_end_screen(self, victory: bool, score: int, name: str,
                        now: int, notice: str) -> None:
        """Game over / victory screen with the name prompt."""
        self.screen.fill(BG)
        if victory:
            self.text("VICTORY!", 130, YELLOW, center=(WIDTH // 2, 150))
            self.text("Congratulations, all levels completed!", 44, WHITE,
                      center=(WIDTH // 2, 250))
        else:
            self.text("GAME OVER", 130, RED, center=(WIDTH // 2, 150))
        self.text(f"Final score: {score}", 64, WHITE,
                  center=(WIDTH // 2, 380))
        if notice:
            self.text(notice, 30, RED, center=(WIDTH // 2, 450))
        self.text("Enter your name:", 44, YELLOW, center=(WIDTH // 2, 530))
        cursor = "_" if (now // 500) % 2 == 0 else " "
        self.text(name + cursor, 80, WHITE, center=(WIDTH // 2, 620))
        self.text("ENTER: save    ESC: skip", 30, GREY,
                  center=(WIDTH // 2, 780))
