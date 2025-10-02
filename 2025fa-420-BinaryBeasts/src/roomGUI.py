from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt  # Added for alignment and Qt namespace enums
from typing import List, Optional
from src.room import RoomManager
import json
from PyQt5.QtWidgets import QFileDialog


class AddRoomDialog(QtWidgets.QDialog):
    """Simple dialog to add or edit a single room name.

    Previously this was also named RoomGUI, which conflicted with the main
    RoomGUI widget below. The duplicate class name caused the dialog class
    to be overwritten, leading to incorrect instantiation and potential
    runtime errors. Renamed to AddRoomDialog for clarity.
    """

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
    def __init__(self, config: dict, loaded_path: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Room Manager")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        self.manager = RoomManager(config)
        self.loaded_path = loaded_path

        # Title label styled similar to main_gui
        title = QtWidgets.QLabel("Room Manager")
        title.setFont(QFont('Arial', 16, QFont.Bold))
        # Align center using Qt enum from QtCore
        title.setAlignment(Qt.AlignCenter)

        # List of rooms
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setFont(QFont('Arial', 10))

        # Buttons (consistent style)
        def make_btn(text: str) -> QtWidgets.QPushButton:
            b = QtWidgets.QPushButton(text)
            b.setFont(QFont('Arial', 9))
            b.setStyleSheet('padding: 8px; background-color: #4CAF50; color: white; border-radius: 5px;')
            return b

        self.add_btn = make_btn("Add Room")
        self.edit_btn = make_btn("Edit Room")
        self.del_btn = make_btn("Delete Room")
        self.save_btn = make_btn("Save Config")

        # Layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(title)
        main_layout.addWidget(self.list_widget)

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.edit_btn)
        btn_row.addWidget(self.del_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.save_btn)
        main_layout.addLayout(btn_row)

        # Signals
        self.add_btn.clicked.connect(self.add_room)
        self.edit_btn.clicked.connect(self.edit_room)
        self.del_btn.clicked.connect(self.delete_room)
        self.save_btn.clicked.connect(self.save_config)

        self.edit_btn.setEnabled(False)
        self.del_btn.setEnabled(False)
        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)

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

    sample_config = {
        "config": {
            "rooms": ["Room A", "Room B", "Room C"],
            "courses": [{"course_id": "CS1", "room": ["Room A"]}],
            "faculty": [{"name": "F1", "room_preferences": {"Room A": 1}}],
        }
    }

    app = QtWidgets.QApplication(sys.argv)
    w = RoomGUI(sample_config)
    w.show()
    sys.exit(app.exec_())
