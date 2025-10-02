"""Manual test that launches the RoomGUI with a sample config.

Run this with:
    python -m tests.test_roomGUI

This is an interactive test and is not a unit test. It opens the PyQt window so you can exercise Add/Edit/Delete.
"""

import sys
import json
from pathlib import Path

# Ensure the repository root is on sys.path so `import src...` works when this
# test is executed directly (for example: `.venv\Scripts\python.exe -m tests.test_roomGUI`).
repo_root = Path(__file__).resolve().parents[1]
repo_root_str = str(repo_root)
if repo_root_str not in sys.path:
    sys.path.insert(0, repo_root_str)

from PyQt5 import QtWidgets
from src.roomGUI import RoomGUI


def main():
    # Prefer configTest.json at the repository root if available
    root = Path(__file__).resolve().parents[1]
    candidate = root / "configTest.json"
    if candidate.exists():
        try:
            cfg = json.loads(candidate.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"Failed to load {candidate}: {e}")
            cfg = None
    else:
        cfg = None

    if cfg is None:
        # fallback sample
        cfg = {
            "config": {
                "rooms": ["Room A", "Room B", "Room C"],
                "courses": [
                    {"course_id": "CS1", "room": ["Room A", "Room B"]},
                    {"course_id": "CS2", "room": ["Room C"]},
                ],
                "faculty": [
                    {"name": "Prof X", "room_preferences": {"Room A": 10, "Room B": 5}}
                ],
            }
        }

    app = QtWidgets.QApplication(sys.argv)
    # If we loaded from a file, pass that path so Save will overwrite it
    loaded_path = str(candidate) if (candidate.exists() and cfg is not None) else None
    w = RoomGUI(cfg, loaded_path=loaded_path)
    w.show()
    app.exec_()

    print("Final rooms:", cfg["config"]["rooms"])


if __name__ == "__main__":
    main()
