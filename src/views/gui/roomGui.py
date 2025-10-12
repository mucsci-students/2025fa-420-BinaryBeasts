from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from typing import Optional, Any
from src.room import RoomManager
import json
from PyQt5.QtWidgets import QFileDialog


class AddRoomDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Room")
        self.setMinimumSize(280, 120)

        self.input = QtWidgets.QLineEdit()
        self.input.setPlaceholderText("Enter Room name")
        save_btn = QtWidgets.QPushButton("Save")
        cancel_btn = QtWidgets.QPushButton("Cancel")

        # Match main_gui button styling
        btn_style = (
            "padding: 10px; background-color: #4CAF50; color: white; "
            "border-radius: 5px; width: 100px;"
        )
        for b in (save_btn, cancel_btn):
            b.setFont(QFont("Arial", 8))
            b.setStyleSheet(btn_style)

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
    def __init__(self, config: Any, loaded_path: Optional[str] = None, parent=None):
        super().__init__(parent)
        # Window/title to match main_gui feel and allow small size
        self.setWindowTitle("College Course Scheduler - Rooms")
        self.setMinimumSize(360, 260)

        # Build RoomManager with scheduler models only (CombinedConfig or SchedulerConfig)
        try:
            from scheduler.config import CombinedConfig, SchedulerConfig  # type: ignore
        except Exception as e:
            raise TypeError(f"RoomGUI requires scheduler models available: {e}")

        if isinstance(config, CombinedConfig) or isinstance(config, SchedulerConfig):
            self.manager = RoomManager(config)
        else:
            raise TypeError("RoomGUI now only accepts CombinedConfig or SchedulerConfig instances")
        # Path to the file this config was loaded from (if any). If set, Save will
        # overwrite this file instead of prompting for a location.
        self.loaded_path = loaded_path

        self.list_widget = QtWidgets.QListWidget()

        # Buttons
        self.add_btn = QtWidgets.QPushButton("Add Room")
        self.edit_btn = QtWidgets.QPushButton("Edit Room")
        self.del_btn = QtWidgets.QPushButton("Delete Room")
        self.save_btn = QtWidgets.QPushButton("Save Config")

        # Match main_gui fonts and green button style
        btn_style = (
            "padding: 10px; background-color: #4CAF50; color: white; "
            "border-radius: 5px; width: 100px;"
        )
        for b in (self.add_btn, self.edit_btn, self.del_btn, self.save_btn):
            b.setFont(QFont("Arial", 8))
            b.setStyleSheet(btn_style)

        # Layout
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.del_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)

        layout = QtWidgets.QVBoxLayout(self)
        # Add title to match main_gui
        title = QtWidgets.QLabel("College Course Scheduler - Rooms")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
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
        """Prompt for a file path and save the full config dict to that file.

        Returns True if the config was saved successfully, False otherwise.
        """
        # If we have a loaded file path, overwrite it directly. Otherwise ask the user.
        if self.loaded_path:
            path = self.loaded_path
        else:
            options = QFileDialog.Options()
            path, _ = QFileDialog.getSaveFileName(self, "Save Config", "config.json", "JSON Files (*.json);;All Files (*)", options=options)
            if not path:
                return False
        try:
            # Gather combined config for saving via manager
            data = self.manager.to_combined_dict()

            # Optionally validate with CombinedConfig before write
            try:
                from scheduler.config import CombinedConfig  # type: ignore
                data = CombinedConfig.model_validate(data).model_dump()
            except Exception:
                pass

            # Write JSON to disk using standard library for portability
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            # If we saved to a chosen path and we didn't previously have a loaded_path,
            # remember this path as the loaded file for future saves.
            if not self.loaded_path:
                self.loaded_path = path
            QtWidgets.QMessageBox.information(self, "Saved", f"Config saved to {path}")
            return True
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save config: {e}")
            return False

    def closeEvent(self, event):
        """Ask the user whether to save before exiting.

        Options: Save, Don't Save, Cancel
        - Save: attempt to save; close only if successful
        - Don't Save: close without saving
        - Cancel: abort close
        """
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle("Confirm Exit")
        msg.setText("Do you want to save your changes before exiting?")
        msg.setIcon(QtWidgets.QMessageBox.Question)
        msg.setStandardButtons(
            QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel
        )
        msg.setDefaultButton(QtWidgets.QMessageBox.Save)
        choice = msg.exec_()

        if choice == QtWidgets.QMessageBox.Save:
            if self.save_config():
                event.accept()
            else:
                # Save canceled or failed; stay open
                event.ignore()
        elif choice == QtWidgets.QMessageBox.Discard:
            event.accept()
        else:
            # Cancel
            event.ignore()


if __name__ == "__main__":
    import sys
    from scheduler.config import SchedulerConfig

    # Minimal self-test runner using SchedulerConfig directly
    sched = SchedulerConfig(rooms=["Room A", "Room B"], labs=[], courses=[], faculty=[])
    app = QtWidgets.QApplication(sys.argv)
    w = RoomGUI(sched)
    w.show()
    sys.exit(app.exec_())