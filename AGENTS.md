# Repository Guidelines

## Project Structure & Module Organization
- `src/phasmo_editor/` is the main package; core logic lives in `save_parser.py`, `game_data.py`, `crypto.py`, and `config.py`.
- GUI code is in `src/phasmo_editor/ui/` with tab modules (`general_tab.py`, `equipment_tab.py`, `stats_tab.py`, `settings_tab.py`) and reusable widgets in `src/phasmo_editor/ui/widgets/`.
- Theme assets and styling are in `src/phasmo_editor/theme/` (QSS + theme XML).
- CLI entry points are in `src/phasmo_editor/cli.py` and `src/phasmo_editor/__main__.py`.
- Packaging metadata is in `pyproject.toml`; dependency locks are in `uv.lock`.

## Build, Test, and Development Commands
- `uv sync` installs dependencies from `pyproject.toml` and `uv.lock`.
- `uv run phasmo-editor` launches the GUI app (default mode).
- `uv run phasmo-editor --cli` runs the CLI editor for headless usage.
- `uv run phasmo-editor --file /path/to/SaveFile.txt` targets a custom save file.
- `pip install .` and `phasmo-editor` are the README-supported pip flow.

## Coding Style & Naming Conventions
- Python 3.10+ codebase with type hints and docstrings; follow the existing style.
- Indentation is 4 spaces; keep imports explicit and grouped.
- Use `snake_case` for modules/functions, `PascalCase` for classes, and `UPPER_SNAKE_CASE` for constants (see `PRESTIGE_TITLES`).
- Keep UI-specific constants in `src/phasmo_editor/ui/layout_constants.py`.

## Testing Guidelines
- `pytest` is listed in dev dependencies, but no `tests/` directory exists yet.
- If you add tests, place them in `tests/` and name files `test_*.py`; run with `uv run pytest`.
- No coverage target is documented; include focused tests for save parsing and data transforms.

## Commit & Pull Request Guidelines
- No `.git` history is present in this checkout, so no commit convention can be inferred.
- Use short, imperative commit subjects (e.g., "Add CLI backup warning") and keep scope tight.
- PRs should describe user-visible changes, and include GUI screenshots or CLI output when UI flows change.

## Data & Configuration Notes
- Save files are sensitive; avoid committing real player data. Keep any sample files (e.g., `decrypted_save.json`) sanitized.
