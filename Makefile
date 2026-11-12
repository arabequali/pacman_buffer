CONFIG ?= config.json

.PHONY: install run debug clean lint lint-strict test package

install:
	@uv sync

run:
	@uv run python3 pac-man.py $(CONFIG)

debug:
	@uv run python3 -m pdb pac-man.py $(CONFIG)

clean:
	@find . -type d \( -name __pycache__ -o -name .mypy_cache \
		-o -name .pytest_cache \) -not -path "./.venv/*" \
		-prune -exec rm -rf {} +
	@rm -rf build dist

lint:
	@uv run python3 -m flake8 .
	@uv run python3 -m mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	@uv run python3 -m flake8 .
	@uv run python3 -m mypy . --strict

test:
	@uv run python3 -m pytest -q tests

package:
	@uv run pyinstaller --noconfirm pac-man.spec
	@cp packaging/README.txt dist/pacman/README.txt
	@cp config.json dist/pacman/config.json
	@echo "Package ready in dist/pacman (zip it and push it to itch.io)"
