"""Configuration loading: JSON with comments, clamped to safe values."""

import json
import logging
from pathlib import Path
from typing import Any

from src.models import Config

log = logging.getLogger("pacman.config")

MIN_MAZE = 7
MAX_MAZE = 99

# name: (kind, minimum, maximum). Defaults come from the Config model.
FIELDS: dict[str, tuple[str, float, float]] = {
    "level_1_seed": ("int", 0, 2**31 - 1),
    "level_size_increase": ("int", 0, 30),
    "level_max_size": ("int", MIN_MAZE, MAX_MAZE),
    "level_count": ("int", 1, 99),
    "level_max_time": ("int", 5, 3600),
    "lives": ("int", 1, 99),
    "points_per_pacgum": ("int", 0, 1_000_000),
    "points_per_super_pacgum": ("int", 0, 1_000_000),
    "points_per_ghosts": ("int", 0, 1_000_000),
    "player_speed": ("float", 1.0, 30.0),
    "ghost_speed": ("float", 1.0, 30.0),
    "power_duration": ("float", 0.5, 120.0),
    "ghost_respawn_time": ("float", 0.5, 120.0),
    "cheat_mode": ("bool", 0, 1),
    "highscore_filename_path": ("str", 0, 0),
}

# Alternative key names (suggested by the subject) mapped to ours.
ALIASES: dict[str, str] = {
    "seed": "level_1_seed",
    "level_max_time_seconds": "level_max_time",
    "points_per_ghost": "points_per_ghosts",
    "highscore_filename": "highscore_filename_path",
}


class ConfigError(Exception):
    """Raised when the configuration file cannot be used at all."""


def strip_comments(text: str) -> str:
    """Remove '#', '//' and '/* */' comments that are outside strings.

    Newlines are preserved so JSON error messages keep correct line numbers.
    """
    out: list[str] = []
    i = 0
    in_string = False
    while i < len(text):
        c = text[i]
        if in_string:
            out.append(c)
            if c == "\\" and i + 1 < len(text):
                out.append(text[i + 1])
                i += 1
            elif c == '"':
                in_string = False
        elif c == '"':
            in_string = True
            out.append(c)
        elif c == "#" or text.startswith("//", i):
            while i < len(text) and text[i] != "\n":
                i += 1
            continue
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            end = len(text) if end == -1 else end + 2
            out.append("\n" * text.count("\n", i, end))
            i = end
            continue
        else:
            out.append(c)
        i += 1
    return "".join(out)


def _check(name: str, value: Any, default: Any) -> Any:
    """Return a valid value for `name`, or `default` (and log why)."""
    kind, low, high = FIELDS[name]
    if kind == "bool":
        if isinstance(value, bool):
            return value
        log.warning("config: '%s' must be true/false, using %r",
                    name, default)
        return default
    if kind == "str":
        if isinstance(value, str) and value.strip():
            return value.strip()
        log.warning("config: '%s' must be a non-empty string, using %r",
                    name, default)
        return default
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        log.warning("config: '%s' must be a number, using %r", name, default)
        return default
    if kind == "int":
        if isinstance(value, float):
            if not value.is_integer():
                log.warning("config: '%s' must be an integer, using %r",
                            name, default)
                return default
            value = int(value)
    else:
        value = float(value)
    if value != value:  # NaN
        log.warning("config: '%s' is not a number, using %r", name, default)
        return default
    if value < low or value > high:
        clamped = min(max(value, low), high)
        log.warning("config: '%s'=%r out of range [%s, %s], clamped to %r",
                    name, value, low, high, clamped)
        return clamped
    return value


def _check_size(value: Any, default: list[int]) -> list[int]:
    """Validate the [width, height] of the first level."""
    if (not isinstance(value, list) or len(value) != 2
            or any(isinstance(v, bool) or not isinstance(v, int)
                   for v in value)):
        log.warning("config: 'level_1_size' must be [width, height] "
                    "integers, using %r", default)
        return list(default)
    result = []
    for v in value:
        if v < MIN_MAZE or v > MAX_MAZE:
            clamped = min(max(v, MIN_MAZE), MAX_MAZE)
            log.warning("config: level_1_size value %d out of range "
                        "[%d, %d], clamped to %d",
                        v, MIN_MAZE, MAX_MAZE, clamped)
            v = clamped
        result.append(v)
    return result


def sanitize(raw: Any) -> Config:
    """Build a valid Config from parsed JSON, never raising."""
    defaults = Config()
    if not isinstance(raw, dict):
        log.warning("config: top level must be a JSON object, "
                    "using defaults")
        return defaults
    data: dict[str, Any] = {}
    for raw_key, value in raw.items():
        key = str(raw_key)
        name = ALIASES.get(key, key)
        if name in data and name != key:
            continue
        data[name] = value
    clean: dict[str, Any] = {}
    for name in FIELDS:
        default = getattr(defaults, name)
        if name not in data:
            log.info("config: '%s' missing, using default %r", name, default)
            continue
        clean[name] = _check(name, data[name], default)
    if "level_1_size" in data:
        clean["level_1_size"] = _check_size(data["level_1_size"],
                                            defaults.level_1_size)
    else:
        log.info("config: 'level_1_size' missing, using default %r",
                 defaults.level_1_size)
    known = set(FIELDS) | {"level_1_size"}
    for key in data:
        if key not in known:
            log.info("config: unknown key '%s' ignored", key)
    return Config(**clean)


def load_config(path: Path) -> Config:
    """Read and validate a configuration file.

    Raises ConfigError for problems that prevent any use of the file
    (missing, unreadable, not JSON); bad values are clamped instead.
    """
    if path.suffix.lower() != ".json":
        raise ConfigError(f"'{path}' is not a .json file")
    try:
        with open(path, "r", encoding="utf-8") as file:
            text = file.read()
    except FileNotFoundError:
        raise ConfigError(f"configuration file '{path}' not found")
    except (OSError, UnicodeDecodeError) as exc:
        raise ConfigError(f"cannot read '{path}': {exc}")
    try:
        raw = json.loads(strip_comments(text))
    except json.JSONDecodeError as exc:
        raise ConfigError(
            f"invalid JSON in '{path}' (line {exc.lineno}, "
            f"column {exc.colno}): {exc.msg}")
    return sanitize(raw)
