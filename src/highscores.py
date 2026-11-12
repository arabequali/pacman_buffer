"""Persistent top-10 highscore table stored as a JSON file."""

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

log = logging.getLogger("pacman.highscores")

MAX_ENTRIES = 10
MAX_NAME_LENGTH = 10
DEFAULT_NAME = "Player"


@dataclass
class ScoreEntry:
    """One line of the highscore table."""

    name: str
    score: int


def sanitize_name(name: str) -> str:
    """Keep ASCII letters, digits and spaces; max 10 chars; never empty."""
    kept = "".join(c for c in name if c.isascii()
                   and (c.isalnum() or c == " "))
    kept = kept.strip()[:MAX_NAME_LENGTH].strip()
    return kept or DEFAULT_NAME


class HighscoreManager:
    """Load, update and save the highscores, tolerating any file error."""

    def __init__(self, path: Path) -> None:
        """Remember the file path and load the table."""
        self.path = path
        self.entries: list[ScoreEntry] = []
        self.load()

    @staticmethod
    def _parse(item: Any) -> ScoreEntry | None:
        """Turn one JSON item into an entry, or None if invalid."""
        if not isinstance(item, dict):
            return None
        name, score = item.get("name"), item.get("score")
        if (not isinstance(name, str) or isinstance(score, bool)
                or not isinstance(score, int) or score < 0):
            return None
        return ScoreEntry(sanitize_name(name), score)

    def load(self) -> None:
        """Read the file; any problem results in an empty/partial table."""
        self.entries = []
        try:
            with open(self.path, "r", encoding="utf-8") as file:
                raw = json.load(file)
        except FileNotFoundError:
            return
        except (OSError, ValueError) as exc:
            log.warning("highscores: cannot read '%s' (%s), starting "
                        "with an empty table", self.path, exc)
            return
        items = raw.get("highscores") if isinstance(raw, dict) else raw
        if not isinstance(items, list):
            log.warning("highscores: unexpected format in '%s', ignored",
                        self.path)
            return
        for item in items:
            entry = self._parse(item)
            if entry is None:
                log.warning("highscores: invalid entry skipped: %r", item)
            else:
                self.entries.append(entry)
        self.entries.sort(key=lambda e: e.score, reverse=True)
        del self.entries[MAX_ENTRIES:]

    def save(self) -> bool:
        """Write the table atomically. Returns False on failure."""
        tmp = self.path.with_name(self.path.name + ".tmp")
        data = {"highscores": [{"name": e.name, "score": e.score}
                               for e in self.entries]}
        try:
            with open(tmp, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2)
            os.replace(tmp, self.path)
        except OSError as exc:
            log.warning("highscores: cannot save '%s': %s", self.path, exc)
            return False
        return True

    def qualifies(self, score: int) -> bool:
        """True if `score` would enter the top 10."""
        if score < 0:
            return False
        return (len(self.entries) < MAX_ENTRIES
                or score > self.entries[-1].score)

    def add(self, name: str, score: int) -> int | None:
        """Insert a score, save, and return its 1-based rank (or None)."""
        if isinstance(score, bool) or score < 0:
            return None
        entry = ScoreEntry(sanitize_name(name), score)
        position = len(self.entries)
        for i, other in enumerate(self.entries):
            if score > other.score:
                position = i
                break
        if position >= MAX_ENTRIES:
            return None
        self.entries.insert(position, entry)
        del self.entries[MAX_ENTRIES:]
        self.save()
        return position + 1
