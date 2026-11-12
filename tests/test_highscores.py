"""Tests for the highscore table."""

from pathlib import Path

from src.highscores import HighscoreManager, sanitize_name


def test_name_rules() -> None:
    """Max 10 chars, alphanumeric and spaces only, never empty."""
    assert sanitize_name("  Bob!!<>  ") == "Bob"
    assert sanitize_name("abcdefghijklmnop") == "abcdefghij"
    assert sanitize_name("???") == "Player"
    assert sanitize_name("a b") == "a b"


def test_add_sort_and_persist(tmp_path: Path) -> None:
    """Scores are sorted, trimmed to 10 and saved."""
    path = tmp_path / "h.json"
    manager = HighscoreManager(path)
    for score in range(0, 120, 10):
        manager.add("p", score)
    assert len(manager.entries) == 10
    assert manager.entries[0].score == 110
    assert manager.add("low", 0) is None
    assert manager.add("top", 500) == 1
    again = HighscoreManager(path)
    assert [e.score for e in again.entries] == [
        e.score for e in manager.entries]


def test_corrupted_files(tmp_path: Path) -> None:
    """Broken or odd files never crash."""
    path = tmp_path / "h.json"
    path.write_text("not json")
    assert HighscoreManager(path).entries == []
    path.write_text('{"highscores": [{"name": "a", "score": -1},'
                    ' {"name": "b", "score": 5}, 3, "x"]}')
    entries = HighscoreManager(path).entries
    assert [(e.name, e.score) for e in entries] == [("b", 5)]
    path.write_text("[1, 2]")
    assert HighscoreManager(path).entries == []


def test_unwritable(tmp_path: Path) -> None:
    """A path that cannot be written is tolerated."""
    manager = HighscoreManager(tmp_path / "missing_dir" / "h.json")
    assert manager.add("a", 10) == 1
    assert manager.save() is False
