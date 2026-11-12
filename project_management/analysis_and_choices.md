# Project analysis and choices

| Subject requirement | Choice | Why |
|---|---|---|
| Python, flake8, mypy | Python 3.12, `Makefile` lint rules, `.flake8` and mypy config exclude the assigned wheel folder | The generator package must stay untouched and is not ours to lint |
| MLX-like library | pygame, restricted to window / blit / fill / text / events; scaling and rotation isolated in `src/assets.py` | Keep a possible port to MLX small |
| A-Maze-ing package as-is | Thin wrapper `Maze.generate`, `perfect=False` | The loader adapts to the package, as required |
| Config with comments | Own comment stripper (`#`, `//`, `/* */`, string aware) + clamping | Required by V.2/V.3; the config changes at defense |
| Highscores | JSON file, atomic save, strict validation | Robust to file errors, human readable |
| Game logic | No pygame in `game/maze/objects` | Testable without a window; deterministic with a seeded `random.Random` |
| Movement | Continuous, time based, buffered direction | Smooth rendering, frame-rate independent |
| Time limit | Lose a life and restart the clock; eaten pacgums stay eaten | Simple rule that prevents score farming |
| Level time | `level_max_time` scales with the maze area | A greedy bot needs about 0.6x of the limit on level 1 (measured: 142 s of 240 s) |
| Cheat mode | Key toggle in menu or config; 7 cheats covering every feature | Lets a reviewer reach any situation in seconds |
| Packaging | PyInstaller one-folder + butler | Works on itch.io; needs one build per OS |
