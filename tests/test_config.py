"""Tests for configuration loading."""

from pathlib import Path

import pytest

from src.config import ConfigError, load_config, sanitize, strip_comments


def write(tmp_path: Path, text: str, name: str = "c.json") -> Path:
    """Write a config file and return its path."""
    path = tmp_path / name
    path.write_text(text)
    return path


def test_comments_are_removed() -> None:
    """#, // and /* */ comments are ignored, strings are kept."""
    text = '# a\n{"a": "x#y", // c\n/* b\n c */ "b": 1}'
    import json
    assert json.loads(strip_comments(text)) == {"a": "x#y", "b": 1}


def test_load_with_comments(tmp_path: Path) -> None:
    """A commented file loads normally."""
    path = write(tmp_path, '# hi\n{"lives": 5}\n')
    assert load_config(path).lives == 5


def test_missing_file(tmp_path: Path) -> None:
    """A missing file is a clean error."""
    with pytest.raises(ConfigError):
        load_config(tmp_path / "nope.json")


def test_not_json_extension(tmp_path: Path) -> None:
    """Only .json files are accepted."""
    with pytest.raises(ConfigError):
        load_config(write(tmp_path, "{}", "c.txt"))


def test_invalid_json(tmp_path: Path) -> None:
    """Broken JSON gives a clean error with the line number."""
    with pytest.raises(ConfigError, match="line"):
        load_config(write(tmp_path, '{"lives": }'))


def test_bad_values_fall_back() -> None:
    """Invalid values are clamped or replaced by defaults."""
    cfg = sanitize({"lives": -4, "points_per_pacgum": "ten",
                    "level_1_size": [2, "x"], "player_speed": 1e9,
                    "cheat_mode": "yes", "unknown": 1})
    assert cfg.lives == 1
    assert cfg.points_per_pacgum == 10
    assert cfg.level_1_size == [29, 29]
    assert cfg.player_speed == 30.0
    assert cfg.cheat_mode is False


def test_non_object_and_aliases() -> None:
    """Wrong top level uses defaults, aliases are understood."""
    assert sanitize([1, 2]).lives == 3
    assert sanitize({"seed": 7, "points_per_ghost": 9}).level_1_seed == 7
    assert sanitize({"points_per_ghost": 9}).points_per_ghosts == 9
