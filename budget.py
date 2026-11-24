"""Launcher: run `python budget.py <command>` from the project root."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from budget_manager.cli import main  # noqa: E402

sys.exit(main())
