"""Command line entry point: python3 pac-man.py config.json"""

import logging
import sys
from pathlib import Path

from src.config import ConfigError, load_config

USAGE = "usage: python3 pac-man.py <config.json>"


def main(argv: list[str]) -> int:
    """Run the game; returns the process exit code (never a traceback)."""
    logging.basicConfig(level=logging.INFO, stream=sys.stderr,
                        format="%(levelname)s: %(message)s")
    args = argv[1:]
    if len(args) == 0 and getattr(sys, "frozen", False):
        args = [str(Path(sys.executable).parent / "config.json")]
    if len(args) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    path = Path(args[0])
    try:
        config = load_config(path)
    except ConfigError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    highscore_path = Path(config.highscore_filename_path)
    if not highscore_path.is_absolute():
        highscore_path = path.resolve().parent / highscore_path
    try:
        from src.app import App
        App(config, highscore_path).run()
    except KeyboardInterrupt:
        return 130
    except Exception as exc:  # last resort: never show a traceback
        logging.getLogger("pacman").error("fatal: %s: %s",
                                          type(exc).__name__, exc)
        return 1
    return 0
