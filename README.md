# flet-habitos

> Habit tracker with streaks, heatmap calendar and CSV export.

[![CI](https://github.com/dblzroch/flet-habitos/actions/workflows/ci.yml/badge.svg)](https://github.com/dblzroch/flet-habitos/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](pyproject.toml)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

Habit tracker desktop app built with [Flet](https://flet.dev/). Track daily habits,
visualize streaks with a heatmap calendar and export your data to CSV.

## Quickstart

```bash
# Clone
git clone https://github.com/dblzroch/flet-habitos.git
cd flet-habitos

# Install (uv)
uv sync --dev

# Run the desktop app
uv run flet-habitos
```

## How it works

- **UI**: Flet (Flutter-based) desktop/mobile GUI.
- **Storage**: SQLite database for habits and daily check-ins.
- **Features**: Create habits, check-in/daily toggle, streak counter,
  heatmap calendar (last 30 days), CSV export.
- **Tests**: `pytest` with coverage gate at 80%.
- **CI**: GitHub Actions runs ruff, mypy and pytest on every push/PR.

## Tests & quality

```bash
make test      # pytest with coverage
make lint      # ruff + mypy
make fmt       # ruff format
```

## License

MIT
