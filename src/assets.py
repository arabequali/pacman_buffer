"""Image loading, trimming, scaling and rotation (the only module that
touches pygame.transform)."""

import logging
import sys
from pathlib import Path

import pygame

log = logging.getLogger("pacman.assets")

REQUIRED = [
    "player.png", "pacgum.png", "super_pacgum.png", "score.png",
    "horizontal_walls.png", "vertical_walls.png",
    "ghost_red.png", "ghost_pink.png", "ghost_cyan.png",
    "ghost_orange.png", "ghost_scared.png",
    "play_button.png", "play_button_cursor.png",
    "highscores_button.png", "highscores_button_cursor.png",
    "instructions_button.png", "instructions_button_cursor.png",
    "exit_button.png", "exit_button_cursor.png",
]


def base_dir() -> Path:
    """Folder holding assets/ (project root, or the PyInstaller bundle)."""
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parent.parent


class Asset:
    """One image, with cached scaled/rotated copies."""

    def __init__(self, name: str, image: pygame.Surface) -> None:
        """Wrap an already loaded surface."""
        self.name = name
        self.image = image
        self._cache: dict[tuple[int, int, int], pygame.Surface] = {}

    def trimmed(self) -> "Asset":
        """Copy without the transparent border around the drawing."""
        rect = self.image.get_bounding_rect()
        if rect.width == 0 or rect.height == 0:
            return self
        return Asset(self.name, self.image.subsurface(rect).copy())

    def scaled(self, width: int, height: int,
               angle: int = 0) -> pygame.Surface:
        """Surface of the given size, rotated counter-clockwise."""
        key = (max(1, width), max(1, height), angle)
        if key not in self._cache:
            surface = pygame.transform.smoothscale(self.image, key[:2])
            if angle:
                surface = pygame.transform.rotate(surface, angle)
            self._cache[key] = surface
        return self._cache[key]


class Assets:
    """All the images of the game, loaded once."""

    def __init__(self, directory: Path | None = None) -> None:
        """Load every required image (a missing one is replaced)."""
        self.directory = directory or base_dir() / "assets"
        self.assets: dict[str, Asset] = {}
        for name in REQUIRED:
            self.get_asset(name)

    def _load(self, name: str) -> Asset:
        """Load one file, falling back to a magenta square."""
        try:
            image = pygame.image.load(str(self.directory / name))
            return Asset(name, image.convert_alpha())
        except (pygame.error, FileNotFoundError, OSError) as exc:
            log.warning("assets: cannot load '%s' (%s), using a "
                        "placeholder", name, exc)
            image = pygame.Surface((32, 32))
            image.fill((255, 0, 255))
            return Asset(name, image)

    def get_asset(self, name: str) -> Asset:
        """Return the asset called `name` (loading it if needed)."""
        if name not in self.assets:
            self.assets[name] = self._load(name)
        return self.assets[name]
