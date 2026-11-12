"""Main loop: menus, game, pause and end-of-game screens."""

import logging
from enum import Enum
from pathlib import Path

import pygame

from src.assets import Assets
from src.display import Display
from src.game import Game, GameState
from src.highscores import HighscoreManager
from src.maze import MazeError
from src.menus import MainMenu, NameInput, PauseMenu
from src.models import Config
from src.objects import Direction

log = logging.getLogger("pacman.app")

KEYS: dict[int, Direction] = {
    pygame.K_UP: Direction.UP, pygame.K_w: Direction.UP,
    pygame.K_z: Direction.UP,
    pygame.K_DOWN: Direction.DOWN, pygame.K_s: Direction.DOWN,
    pygame.K_LEFT: Direction.LEFT, pygame.K_a: Direction.LEFT,
    pygame.K_q: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT, pygame.K_d: Direction.RIGHT,
}
VALIDATE = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)
MAX_DT = 1 / 30


class Screen(Enum):
    """The screen currently shown."""

    MENU = 1
    HIGHSCORES = 2
    INSTRUCTIONS = 3
    PLAYING = 4
    PAUSED = 5
    END = 6


class App:
    """Owns the window and routes events to the current screen."""

    def __init__(self, config: Config, highscore_path: Path,
                 assets_dir: Path | None = None) -> None:
        """Initialise pygame, the assets and the highscores."""
        self.config = config
        pygame.init()
        self.display = make_display(assets_dir)
        self.highscores = HighscoreManager(highscore_path)
        self.menu = MainMenu()
        self.pause_menu = PauseMenu()
        self.name_input = NameInput()
        self.screen = Screen.MENU
        self.game: Game | None = None
        self.cheat = config.cheat_mode
        self.notice = ""
        self.end_notice = ""
        self.running = True
        self.clock = pygame.time.Clock()

    # ------------------------------------------------------------ flow
    def run(self) -> None:
        """Loop until the window is closed or Exit is chosen."""
        while self.running:
            dt = min(self.clock.tick(60) / 1000.0, MAX_DT)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.on_key(event)
            self.update(dt)
            self.draw()
        pygame.quit()

    def start_game(self) -> None:
        """Create a new run, reporting generator failures in the menu."""
        try:
            self.game = Game(self.config, cheat=self.cheat)
        except MazeError as exc:
            self.notice = f"Cannot start: {exc}"
            self.game = None
            return
        self.notice = ""
        self.screen = Screen.PLAYING

    def update(self, dt: float) -> None:
        """Advance the running game."""
        if self.screen != Screen.PLAYING or self.game is None:
            return
        self.game.update(dt)
        if self.game.state in (GameState.GAME_OVER, GameState.VICTORY):
            self.name_input = NameInput()
            self.end_notice = self.game.error and (
                "Generator error: " + self.game.error) or ""
            self.screen = Screen.END

    def finish_end_screen(self, save: bool) -> None:
        """Save the score (optionally) and go back to the menu."""
        if self.game is not None and save:
            rank = self.highscores.add(self.name_input.text,
                                       self.game.score)
            self.notice = (f"Score saved: rank #{rank}" if rank
                           else "Score too low for the top 10")
        else:
            self.notice = ""
        self.game = None
        self.screen = Screen.MENU

    # ------------------------------------------------------------ input
    def on_key(self, event: pygame.event.Event) -> None:
        """Dispatch a key press to the current screen."""
        key = event.key
        if self.screen == Screen.MENU:
            self.key_menu(key)
        elif self.screen in (Screen.HIGHSCORES, Screen.INSTRUCTIONS):
            if key in VALIDATE or key == pygame.K_ESCAPE:
                self.screen = Screen.MENU
        elif self.screen == Screen.PLAYING:
            self.key_playing(key)
        elif self.screen == Screen.PAUSED:
            self.key_paused(key)
        elif self.screen == Screen.END:
            self.key_end(event)

    def key_menu(self, key: int) -> None:
        """Main menu navigation."""
        if key in (pygame.K_UP, pygame.K_w, pygame.K_z):
            self.menu.move(-1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.menu.move(1)
        elif key == pygame.K_c:
            self.cheat = not self.cheat
        elif key == pygame.K_ESCAPE:
            self.running = False
        elif key in VALIDATE:
            choice = self.menu.selected
            self.notice = ""
            if choice == "play":
                self.start_game()
            elif choice == "highscores":
                self.screen = Screen.HIGHSCORES
            elif choice == "instructions":
                self.screen = Screen.INSTRUCTIONS
            else:
                self.running = False

    def key_playing(self, key: int) -> None:
        """Movement, pause and cheat keys."""
        game = self.game
        if game is None:
            return
        if key in KEYS:
            game.set_direction(KEYS[key])
        elif key in (pygame.K_p, pygame.K_ESCAPE):
            self.pause_menu.cursor = 0
            self.screen = Screen.PAUSED
        elif game.cheat_enabled:
            actions = {
                pygame.K_i: game.cheat_toggle_invincible,
                pygame.K_n: game.cheat_skip_level,
                pygame.K_g: game.cheat_toggle_freeze,
                pygame.K_l: game.cheat_add_life,
                pygame.K_v: game.cheat_toggle_speed,
                pygame.K_e: game.cheat_power,
                pygame.K_t: game.cheat_low_time,
            }
            if key in actions:
                actions[key]()

    def key_paused(self, key: int) -> None:
        """Pause menu."""
        if key in (pygame.K_UP, pygame.K_w, pygame.K_z):
            self.pause_menu.move(-1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.pause_menu.move(1)
        elif key in (pygame.K_p, pygame.K_ESCAPE):
            self.screen = Screen.PLAYING
        elif key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
            if self.pause_menu.selected == "resume":
                self.screen = Screen.PLAYING
            else:
                self.game = None
                self.notice = ""
                self.screen = Screen.MENU

    def key_end(self, event: pygame.event.Event) -> None:
        """Name entry after game over / victory."""
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.finish_end_screen(save=True)
        elif event.key == pygame.K_ESCAPE:
            self.finish_end_screen(save=False)
        elif event.key == pygame.K_BACKSPACE:
            self.name_input.backspace()
        else:
            self.name_input.type_char(event.unicode)

    # ------------------------------------------------------------- draw
    def instructions(self) -> list[str]:
        """Text of the instructions screen."""
        cfg = self.config
        lines = [
            "#Controls",
            "Arrows, WASD or ZQSD : move Pac-Man",
            "P or ESC : pause        C (main menu) : cheat mode",
            "#Rules",
            "Eat every pacgum to clear the level.",
            f"Pacgum: {cfg.points_per_pacgum} pts   "
            f"Super-pacgum: {cfg.points_per_super_pacgum} pts   "
            f"Ghost: {cfg.points_per_ghosts} pts",
            "Super-pacgums sit in the 4 corners: ghosts become edible",
            "for a few seconds. Eat them before they come back!",
            "A ghost touching you costs one life. "
            f"You start with {cfg.lives}.",
            "Each level has a time limit: when it runs out you lose",
            "a life and the clock restarts.",
            f"Clear all {cfg.level_count} levels to win.",
            "#Cheat mode (for evaluation)",
            "I invincible   N next level   G freeze ghosts",
            "L extra life   V speed   E edible ghosts   T low time",
        ]
        return lines

    def draw(self) -> None:
        """Draw the current screen."""
        now = pygame.time.get_ticks()
        d = self.display
        if self.screen == Screen.MENU:
            d.draw_main_menu(self.menu, self.highscores.entries,
                             self.cheat, self.notice, now)
        elif self.screen == Screen.HIGHSCORES:
            d.draw_highscores(self.highscores.entries)
        elif self.screen == Screen.INSTRUCTIONS:
            d.draw_instructions(self.instructions())
        elif self.screen in (Screen.PLAYING, Screen.PAUSED):
            if self.game is not None:
                d.draw_game(self.game, now, True)
            if self.screen == Screen.PAUSED:
                d.draw_pause(self.pause_menu)
        elif self.screen == Screen.END and self.game is not None:
            d.draw_end_screen(self.game.state == GameState.VICTORY,
                              self.game.score, self.name_input.text, now,
                              self.end_notice)
        d.flip()


def make_display(assets_dir: Path | None) -> Display:
    """Build the window and the assets (after pygame.init)."""
    pygame.display.init()
    pygame.font.init()
    pygame.display.set_mode((1, 1))
    return Display(Assets(assets_dir))
