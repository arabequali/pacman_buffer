"""Menu navigation and text input (logic only)."""

from src.highscores import MAX_NAME_LENGTH


class Menu:
    """A vertical list of entries with a cursor."""

    def __init__(self, entries: list[str]) -> None:
        """Create a menu; the cursor starts on the first entry."""
        self.entries = entries
        self.cursor = 0

    def move(self, delta: int) -> None:
        """Move the cursor (wraps around)."""
        self.cursor = (self.cursor + delta) % len(self.entries)

    @property
    def selected(self) -> str:
        """Identifier of the entry under the cursor."""
        return self.entries[self.cursor]


class MainMenu(Menu):
    """Start Game / View Highscores / Instructions / Exit."""

    def __init__(self) -> None:
        """Create the main menu."""
        super().__init__(["play", "highscores", "instructions", "exit"])


class PauseMenu(Menu):
    """Resume / Return to the main menu."""

    LABELS = {"resume": "Resume the game", "menu": "Return to main menu"}

    def __init__(self) -> None:
        """Create the pause menu."""
        super().__init__(["resume", "menu"])


class NameInput:
    """Name typed at the end of a game (letters, digits and spaces)."""

    def __init__(self) -> None:
        """Start with an empty name."""
        self.text = ""

    def type_char(self, char: str) -> None:
        """Add a character if it is allowed and there is room."""
        if (len(char) == 1 and char.isascii()
                and (char.isalnum() or char == " ")
                and len(self.text) < MAX_NAME_LENGTH):
            self.text += char

    def backspace(self) -> None:
        """Delete the last character."""
        self.text = self.text[:-1]
