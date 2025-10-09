from PyQt5 import QtWidgets
from typing import List, Optional
import json
from PyQt5.QtWidgets import QFileDialog

# Import RoomManager in a way that works when running `python -m src.main_gui`
try:
    from src.room import RoomManager  # preferred when src is a package
except Exception:
    from room import RoomManager  # fallback when running from src directory


class AddRoomDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Room")
        self.resize(300, 100)

        self.input = QtWidgets.QLineEdit()
        self.input.setPlaceholderText("Enter Room name")
        save_btn = QtWidgets.QPushButton("Save")
        cancel_btn = QtWidgets.QPushButton("Cancel")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.input)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

    def get_room_name(self) -> str:
        return self.input.text().strip()


class RoomGUI(QtWidgets.QWidget):
    def __init__(self, config, loaded_path: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Room Manager")
        self.resize(400, 300)

        self.manager = RoomManager(config)
        # Path to the file this config was loaded from (if any). If set, Save will
        # overwrite this file instead of prompting for a location.
        self.loaded_path = loaded_path

        self.list_widget = QtWidgets.QListWidget()

        # Buttons
        self.add_btn = QtWidgets.QPushButton("Add Room")
        self.edit_btn = QtWidgets.QPushButton("Edit Room")
        self.del_btn = QtWidgets.QPushButton("Delete Room")
        self.save_btn = QtWidgets.QPushButton("Save Config")

        # Layout
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.del_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.list_widget)
        layout.addLayout(btn_layout)

        # Signals
        self.add_btn.clicked.connect(self.add_room)
        self.edit_btn.clicked.connect(self.edit_room)
        self.del_btn.clicked.connect(self.delete_room)
        self.save_btn.clicked.connect(self.save_config)

        # Disable edit/delete when no selection
        self.edit_btn.setEnabled(False)
        self.del_btn.setEnabled(False)
        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)

        # populate list
        self.refresh()

    def refresh(self):
        self.list_widget.clear()
        for r in self.manager.get_rooms():
            self.list_widget.addItem(r)
        # Update button enabled state after refreshing the list
        self._on_selection_changed()

    def add_room(self):
        dlg = AddRoomDialog(self)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            name = dlg.get_room_name()
            if not name:
                QtWidgets.QMessageBox.warning(self, "Invalid", "Room name cannot be empty")
                return
            added = self.manager.add_room(name)
            if not added:
                QtWidgets.QMessageBox.information(self, "Exists", f"Room '{name}' already exists")
            self.refresh()

    def edit_room(self):
        item = self.list_widget.currentItem()
        if not item:
            QtWidgets.QMessageBox.information(self, "Select", "Select a room from the list to edit.")
            return
        old = item.text()
        dlg = AddRoomDialog(self)
        dlg.input.setText(old)
        dlg.setWindowTitle("Edit Room")
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            new = dlg.get_room_name()
            if not new:
                QtWidgets.QMessageBox.warning(self, "Invalid", "Room name cannot be empty")
                return
            success = self.manager.edit_room(old, new)
            if not success:
                QtWidgets.QMessageBox.information(self, "Failed", "Edit failed (maybe new name exists)")
            self.refresh()

    def delete_room(self):
        item = self.list_widget.currentItem()
        if not item:
            QtWidgets.QMessageBox.information(self, "Select", "Select a room from the list to delete.")
            return
        rm = item.text()
        confirm = QtWidgets.QMessageBox.question(
            self,
            "Confirm",
            f"Delete room '{rm}'? This will remove references in courses and faculty.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        )
        if confirm == QtWidgets.QMessageBox.Yes:
            self.manager.delete_room(rm)
            self.refresh()

    def _on_selection_changed(self):
        """Enable or disable edit/delete buttons based on selection."""
        item = self.list_widget.currentItem()
        has = bool(item)
        self.edit_btn.setEnabled(has)
        self.del_btn.setEnabled(has)

    def save_config(self):
        """Prompt for a file path and save the full config dict to that file."""
        # If we have a loaded file path, overwrite it directly. Otherwise ask the user.
        if self.loaded_path:
            path = self.loaded_path
        else:
            options = QFileDialog.Options()
            path, _ = QFileDialog.getSaveFileName(self, "Save Config", "config.json", "JSON Files (*.json);;All Files (*)", options=options)
            if not path:
                return
        try:
            # The RoomManager stores the config dict by reference. Prefer to validate
            # and serialize using the scheduler package's CombinedConfig if available
            # (keeps Pydantic serialization rules), otherwise fall back to a plain JSON dump.
            try:
                # Try to import the scheduler CombinedConfig for validation/serialization
                from scheduler.config import CombinedConfig  # type: ignore

                # Attempt to construct/validate a CombinedConfig and then dump
                combined = CombinedConfig.model_validate(self.manager.config)
                data = combined.model_dump()
            except Exception:
                # If scheduler isn't importable or validation fails, fallback to raw dict
                data = self.manager.config

            # Write JSON to disk using standard library for portability
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            # If we saved to a chosen path and we didn't previously have a loaded_path,
            # remember this path as the loaded file for future saves.
            if not self.loaded_path:
                self.loaded_path = path
            QtWidgets.QMessageBox.information(self, "Saved", f"Config saved to {path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save config: {e}")


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    sample = {"config": {"rooms": ["Room A"], "courses": [], "faculty": []}}
    w = RoomGUI(sample)
    w.show()
    sys.exit(app.exec_())