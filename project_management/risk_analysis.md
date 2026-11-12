# Risk analysis

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| Config changed during the defense with odd values | crash | high | Every key validated and clamped, unit tests in `tests/test_config.py` |
| Assigned maze package fails or changes | no level | medium | Wrapper validates the grid, 3 retries, clean message |
| Corrupted highscore file | crash at start | medium | Loader skips invalid entries, never raises |
| Reviewer cannot reach late levels | cannot check features | high | Cheat mode (skip level, invincibility, freeze) |
| Level too big or too long | unplayable | medium | `level_max_size` cap, time scaled with area |
| Team member cannot explain generated code | failed evaluation | medium | Read and explain each module together before the review |
| Package missing on the platform / wrong OS | no demo | medium | `make package` rehearsed, build per OS, test the downloaded build |
| Placeholder assets left in the final build | ugly demo | medium | List in README of this folder; replace before publishing |
