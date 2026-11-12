# Acceptance test plan

"Auto" = covered by `make test` or scripted headless runs done during
development. "Manual" = to be checked by a human with the real window.

| # | Feature (subject) | How | Result |
|---|---|---|---|
| 1 | Exactly one argument; clean errors | CLI run with 0, 2 args, missing file, bad JSON, `.txt` | pass (auto) |
| 2 | Config comments, defaults, clamping, unknown keys | `tests/test_config.py` | pass (auto) |
| 3 | Level 1 uses seed 42, others random | `test_seed_is_reproducible`, `test_level_specs` | pass (auto) |
| 4 | 4 ghosts in corners, 4 super-pacgums, player in middle | `test_initial_state` | pass (auto) |
| 5 | Pacgum / super-pacgum / ghost scores | `test_player_eats_and_scores`, `test_edible_ghost_is_eaten` | pass (auto) |
| 6 | Life lost on ghost touch, game over | `test_ghost_collision_and_game_over` | pass (auto) |
| 7 | Time limit | `test_time_out_costs_a_life` | pass (auto) |
| 8 | 10 levels, victory, score/lives kept | `test_skip_all_levels_to_victory` (3 levels) + scripted flow | pass (auto) |
| 9 | Entities never enter walls | `test_player_cannot_cross_walls` (1500 steps) | pass (auto) |
| 10 | Highscore: top 10, names, corrupted file | `tests/test_highscores.py` | pass (auto) |
| 11 | Menus, pause, name entry, back to menu | scripted key events (headless) | pass (auto) |
| 12 | Packaged executable starts | built with `make package`, run headless 6 s | pass (auto) |
| 13 | Look and feel with the final assets, ghost AI feel | play 2 levels | to do (manual) |
| 14 | Real keyboard (arrows, WASD, ZQSD) | play | to do (manual) |
| 15 | Download and run the build from itch.io | fresh machine | to do (manual) |

## Bugs found and fixed
- Reversing exactly on a cell centre moved the entity by one cell (fixed in `Moving.reverse`).
