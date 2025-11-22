"""Pytest configuration for test session.

Ensures the project root is on sys.path so imports like `from src...` work
both locally and in CI without requiring an editable install.
"""
from __future__ import annotations

import sys
from pathlib import Path


def _ensure_project_root_on_sys_path() -> None:
    # tests/ -> project root
    root = Path(__file__).resolve().parents[1]
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


_ensure_project_root_on_sys_path()
