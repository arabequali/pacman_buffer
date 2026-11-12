"""Allow `python3 -m src config.json`."""

import sys

from src.cli import main

sys.exit(main(["pac-man"] + sys.argv[1:]))
