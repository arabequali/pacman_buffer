#!/usr/bin/env python3
"""Pac-Man. Usage: python3 pac-man.py config.json"""

import sys

from src.cli import main

if __name__ == "__main__":
    sys.exit(main(sys.argv))
