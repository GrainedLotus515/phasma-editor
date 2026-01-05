"""
Entry point for PhasmoEditor.

Supports both GUI and CLI modes:
    phasmo-editor           # Launch GUI
    phasmo-editor --cli     # Launch CLI mode
"""

import argparse
import sys
from pathlib import Path


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="phasmo-editor",
        description="Phasmophobia Save Editor - Edit your save file with a modern GUI or CLI",
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run in CLI mode (no GUI)",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=Path,
        default=None,
        help="Path to save file (uses default location if not specified)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    args = parser.parse_args()

    if args.cli:
        # CLI mode
        from .cli import run_cli

        return run_cli(args.file)
    else:
        # GUI mode
        return run_gui(args.file)


def run_gui(save_path: Path | None) -> int:
    """Run the GUI application."""
    try:
        from PySide6.QtWidgets import QApplication

        from .ui import MainWindow
    except ImportError as e:
        print(f"Error: Failed to import GUI dependencies: {e}")
        print("Make sure PySide6 is installed: uv pip install PySide6")
        return 1

    app = QApplication(sys.argv)
    app.setApplicationName("PhasmoEditor")
    app.setApplicationDisplayName("PhasmoEditor")

    window = MainWindow(save_path)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
