"""Manual test that launches the RoomGUI with a scheduler model.

Run this with:
    python -m tests.test_roomGUI

This is an interactive test and is not a unit test. It opens the PyQt window so you can exercise Add/Edit/Delete.
"""

import sys
from pathlib import Path

# Ensure the repository root is on sys.path so `import src...` works when this
# test is executed directly (for example: `.venv\Scripts\python.exe -m tests.test_roomGUI`).
repo_root = Path(__file__).resolve().parents[1]
repo_root_str = str(repo_root)
if repo_root_str not in sys.path:
    sys.path.insert(0, repo_root_str)

from PyQt5 import QtWidgets
from src.views.gui.roomGui import RoomGUI
from scheduler.config import CombinedConfig, SchedulerConfig
from scheduler import load_config_from_file


def main():
    # Prefer configTest.json at the repository root if available
    root = Path(__file__).resolve().parents[1]
    candidate = root / "configTest.json"

    model: CombinedConfig | SchedulerConfig
    loaded_path: str | None = None
    if candidate.exists():
        try:
            model = load_config_from_file(CombinedConfig, str(candidate))
            loaded_path = str(candidate)
        except Exception as e:
            print(f"Failed to load CombinedConfig from {candidate}: {e}")
            # fall back to minimal scheduler config
            model = SchedulerConfig(rooms=["Room A", "Room B", "Room C"], labs=[], courses=[], faculty=[])
    else:
        # fallback minimal scheduler config (no cross-references, safest for manual UI test)
        model = SchedulerConfig(rooms=["Room A", "Room B", "Room C"], labs=[], courses=[], faculty=[])

    app = QtWidgets.QApplication(sys.argv)
    w = RoomGUI(model, loaded_path=loaded_path)
    w.show()
    app.exec_()

    # Show final rooms from the same model instance
    final_rooms = model.config.rooms if isinstance(model, CombinedConfig) else model.rooms
    print("Final rooms:", final_rooms)


if __name__ == "__main__":
    main()
