# PhasmoEditor

A Python tool for editing Phasmophobia save files with a modern GUI.

## Features

- Edit money, level, experience, and prestige
- Modern Catppuccin Mocha themed interface
- Automatic save file detection (Windows & Linux/Proton)
- Automatic backup creation
- CLI mode for headless usage

## Installation

```bash
# Using uv (recommended)
uv sync
uv run phasmo-editor

# Or install with pip
pip install .
phasmo-editor
```

## Usage

### GUI Mode (default)
```bash
phasmo-editor
```

### CLI Mode
```bash
phasmo-editor --cli
```

### Custom Save File
```bash
phasmo-editor --file /path/to/SaveFile.txt
```

## Disclaimer

This tool is for educational purposes only. Use responsibly and at your own risk.
Always backup your save files before editing!

## Credits

- Original C# version by [stth12](https://github.com/stth12/PhasmoEditor)
- Python port with GUI enhancements
