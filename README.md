*This project has been created as part of the 42 curriculum by <login1>[, <login2>[, <login3>]].*

# Pac-Man

## Description

A complete, playable Pac-Man written in Python 3.12 with `pygame`.
A maze is generated for every level by the assigned **A-Maze-ing**
package (`mazegenerator`, used as-is), four ghosts with different
behaviours chase the player, super-pacgums make them edible, and a
persistent top-10 highscore table is shown in the main menu.

Features: main menu (Start / Highscores / Instructions / Exit), HUD
(score, lives, level, remaining time), pause menu, game over and victory
screens with name entry, 10 levels, JSON-with-comments configuration,
cheat mode for peer review, packaged build for itch.io.

## Instructions

```
make install        # uv sync (runtime + dev dependencies)
make run            # python3 pac-man.py config.json
make run CONFIG=other.json
make debug          # same, under pdb
make lint           # flake8 + mypy (flags required by the subject)
make lint-strict    # flake8 + mypy --strict
make test           # pytest (tests/ are not part of the grading)
make package        # PyInstaller build in dist/pacman
make clean
```

The program takes **exactly one** argument, a `.json` file:
`python3 pac-man.py config.json`. Errors (missing file, invalid JSON,
invalid values) print a clear message, never a traceback.

**Controls**: arrows, WASD or ZQSD to move; `P` / `Esc` to pause;
`Up/Down` + `Enter` in menus; `C` in the main menu toggles the cheat mode.

**Cheat mode** (also `"cheat_mode": true` in the config). In game:
`I` invincibility, `N` skip level, `G` freeze ghosts, `L` +1 life,
`V` faster player, `E` make ghosts edible, `T` leave only 5 seconds
(to test the time-out). Active cheats are shown in the HUD.

## Configuration

JSON file; lines starting with `#` (and `//`, `/* */`) are comments.
Missing or invalid values are clamped/replaced by the default and a
message is logged on stderr; unknown keys are ignored. The values below
are also what `config.json` contains.

| Key | Default | Range | Meaning |
|---|---|---|---|
| `level_1_seed` | 42 | 0..2^31-1 | Seed of level 1 (0 = random). Other levels are random |
| `level_1_size` | [29, 29] | 7..99 each | [width, height] of level 1 |
| `level_size_increase` | 5 | 0..30 | Cells added to each side per level |
| `level_max_size` | 49 | 7..99 | Cap on the maze side (keeps cells visible) |
| `level_count` | 10 | 1..99 | Number of levels to win the game |
| `level_max_time` | 240 | 5..3600 | Seconds for level 1; later levels scale with the maze area |
| `lives` | 3 | 1..99 | Starting lives |
| `points_per_pacgum` | 10 | >= 0 | Score of a pacgum |
| `points_per_super_pacgum` | 100 | >= 0 | Score of a super-pacgum |
| `points_per_ghosts` | 500 | >= 0 | Score of an edible ghost |
| `player_speed` | 8.0 | 1..30 | Cells per second |
| `ghost_speed` | 6.5 | 1..30 | Cells per second (+4 % per level, edible ghosts 40 % slower) |
| `power_duration` | 8.0 | 0.5..120 | Seconds ghosts stay edible |
| `ghost_respawn_time` | 5.0 | 0.5..120 | Seconds before an eaten ghost reappears in its corner |
| `cheat_mode` | false | | Start with cheat mode on |
| `highscore_filename_path` | highscores.json | | Relative paths are relative to the config file |

Aliases from the subject are understood too: `seed`, `points_per_ghost`,
`highscore_filename`.

## Highscore

`src/highscores.py`. The table is a JSON file
(`{"highscores": [{"name": ..., "score": ...}]}`), loaded when the game
starts and written when the player confirms a name at the end of a game
(game over or victory). Only the 10 best scores are kept, ties keep the
older score first. Names: max 10 characters, ASCII letters, digits and
spaces (anything else is removed; an empty name becomes `Player`).
Scores must be non-negative integers. A missing, corrupted or read-only
file never crashes the game: invalid entries are skipped and a message is
logged. Saving is atomic (temporary file + `os.replace`).
JSON was chosen because it is human readable, easy to validate and
needs no extra dependency.

## Maze Generation

`src/maze.py` wraps `mazegenerator.MazeGenerator` (the package assigned
by another group, installed from `mazegen_wheel/` and **not modified**).
We call it with `perfect=False` (loops, no dead ends) and a seed: level 1
uses `level_1_seed`, the following levels use seed 0 (random).
The loader adapts to its interface: each cell is an int whose bits are the
walls (1 north, 2 east, 4 south, 8 west); `15` marks the isolated cells of
the "42" pattern, which are walls for the game. The wrapper checks the
grid (rectangular, values 0..15, all four corners connected). If generation
fails, it is retried up to 3 times; if it still fails the error is shown
in the menu (level 1) or the game ends cleanly (later levels).

## Implementation

- **Movement** is continuous between cell centres (`progress` from 0 to 1)
  and time based (`dt`), so speed does not depend on the frame rate. The
  wanted direction is buffered and applied at the next junction; reversing
  is immediate.
- **Level**: pacgums on every playable cell, super-pacgums and ghosts in the 4
  corners, player on the playable cell nearest to the centre. The level is
  won when every pacgum is eaten. Score and lives are kept between levels.
- **Ghosts** (BFS distance fields, cached): *blinky* takes the shortest
  path to the player, *pinky* aims 4 cells ahead of the player, *inky* is
  half random, *clyde* chases from far away and returns to his corner when
  closer than 8 cells. When edible they run away (slower). They are
  released one after the other (every 2 s). An eaten ghost reappears in its
  corner after `ghost_respawn_time`.
- **Time limit**: when it runs out the player loses a life, the clock
  restarts and the pacgums already eaten stay eaten (no score farming).
- **Rendering**: walls are pre-drawn once per level; the cell size adapts to
  the maze size. All graphics come from `assets/` (images are trimmed,
  scaled and cached in `src/assets.py`); text uses pygame's default font.
- **Graphics library**: only simple operations are used (window, image
  blit, fill, text, keyboard events). Image scaling/rotation
  (`pygame.transform`) is isolated in `src/assets.py`.

## General Software Architecture

```
pac-man.py ─▶ src/cli.py ─▶ src/config.py ─▶ src/models.py (Config)
                  └────────▶ src/app.py (App: loop, screens, input)
                                ├─ src/display.py (all drawing) ─▶ src/assets.py
                                ├─ src/menus.py (Menu, MainMenu, PauseMenu, NameInput)
                                ├─ src/highscores.py (HighscoreManager)
                                └─ src/game.py (Game: rules, no graphics)
                                      ├─ src/maze.py (Maze ─▶ mazegenerator)
                                      └─ src/objects.py (Direction, Pacgum,
                                         SuperPacgum, Moving ▶ Player, Ghost)
```

`game`, `maze`, `objects`, `config`, `highscores` do not import pygame, so
they are unit-tested (`tests/`) without a window.

## Project Management

See [`project_management/`](project_management/): timeline, analysis and
choices, risk analysis, acceptance test plan, team organisation and
blocking points.

## Packaging

`make package` builds `dist/pacman/` with PyInstaller (assets bundled,
`config.json` and `README.txt` next to the executable). Zip that folder
and upload it to itch.io as a free, **unlisted/restricted** project, for
instance with butler:

```
butler push dist/pacman <itch-user>/<game>:linux      # or :windows / :mac
```

A build must be made on each target OS (PyInstaller does not
cross-compile). Without argument, the packaged game reads the `config.json`
next to the executable.

## Resources

- pygame documentation: https://www.pygame.org/docs/
- Pac-Man ghost behaviour ("The Pac-Man Dossier"):
  https://pacman.holenet.info/
- Python `logging`, `json`, `enum`, `dataclasses`; `mypy` and `flake8` docs
- PyInstaller manual: https://pyinstaller.org/ ; itch.io butler:
  https://itch.io/docs/butler/
- Breadth-first search (shortest paths on a grid)

**Use of AI**: Claude (Anthropic) was used to complete this project from
the subject: restructuring the existing code into modules, the game rules
and ghost AI, configuration/highscore handling, unit tests, packaging
files and the first draft of this documentation. The generated code was
run, linted (flake8, mypy) and tested (pytest, scripted headless runs).
<!-- TEAM: edit this paragraph so it states honestly what you did
yourselves and what was generated, and make sure you can explain every
part of the code during the evaluation. -->
