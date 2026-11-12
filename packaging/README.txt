PAC-MAN
=======

Launch the game: run the "pacman" executable.
It reads "config.json" (next to the executable). To use another file,
start it from a terminal:   ./pacman my_config.json

CONTROLS
  Arrows / WASD / ZQSD : move          P or ESC : pause
  Menu: UP/DOWN + ENTER, C = toggle cheat mode

CHEAT MODE (press C in the main menu, then in game)
  I invincible   N next level   G freeze ghosts   L +1 life
  V speed        E edible ghosts   T only 5 seconds left

CONFIGURATION (config.json, JSON with # comments)
  level_1_seed, level_1_size [w, h], level_size_increase, level_max_size,
  level_count, level_max_time (seconds, level 1), lives,
  points_per_pacgum, points_per_super_pacgum, points_per_ghosts,
  player_speed, ghost_speed, power_duration, ghost_respawn_time,
  cheat_mode, highscore_filename_path.
Invalid or missing values are replaced by safe defaults.

Highscores are stored in highscores.json next to config.json.
