"""Faculty GUI (View) that uses FacultyController for business logic.

The view handles Qt signals, collects user input via dialogs, and calls
the controller methods. The controller remains framework-agnostic and
is imported lazily to avoid package import ordering issues.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, Optional

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont

from src.controllers.faculty_controller import FacultyController


class FacultyDialog(QtWidgets.QDialog):
    """Dialog to add or edit a faculty entry. UI-only; returns raw inputs.
    """

    def __init__(self, parent=None, initial: Dict[str, Any] | None = None):
        super().__init__(parent)
        self.setWindowTitle("Faculty")
        self.initial = initial or {}
        self._build_ui()
        if initial:
            self._load_initial(initial)

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        form = QtWidgets.QFormLayout()
        self.name_edit = QtWidgets.QLineEdit()
        form.addRow("Name:", self.name_edit)

        self.min_edit = QtWidgets.QSpinBox()
        self.min_edit.setRange(0, 100)
        form.addRow("Min credits:", self.min_edit)

        self.max_edit = QtWidgets.QSpinBox()
        self.max_edit.setRange(0, 100)
        form.addRow("Max credits:", self.max_edit)

        self.unique_edit = QtWidgets.QSpinBox()
        self.unique_edit.setRange(1, 20)
        form.addRow("Unique course limit:", self.unique_edit)

        # Times per day (simple single range text per day)
        self.time_edits: Dict[str, QtWidgets.QLineEdit] = {}
        days = ["MON", "TUE", "WED", "THU", "FRI"]
        for d in days:
            le = QtWidgets.QLineEdit()
            le.setPlaceholderText("e.g. 09:00-17:00 or leave blank")
            form.addRow(f"{d}:", le)
            self.time_edits[d] = le

        layout.addLayout(form)

        # Preferences: one KEY:weight per line
        self.course_prefs = QtWidgets.QPlainTextEdit()
        self.course_prefs.setPlaceholderText("CourseID:weight (one per line)")
        layout.addWidget(QtWidgets.QLabel("Course preferences:"))
        layout.addWidget(self.course_prefs)

        self.room_prefs = QtWidgets.QPlainTextEdit()
        self.room_prefs.setPlaceholderText("RoomName:weight (one per line)")
        layout.addWidget(QtWidgets.QLabel("Room preferences:"))
        layout.addWidget(self.room_prefs)

        self.lab_prefs = QtWidgets.QPlainTextEdit()
        self.lab_prefs.setPlaceholderText("LabName:weight (one per line)")
        layout.addWidget(QtWidgets.QLabel("Lab preferences:"))
        layout.addWidget(self.lab_prefs)

        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _load_initial(self, d: Dict[str, Any]):
        self.name_edit.setText(d.get("name", ""))
        self.min_edit.setValue(d.get("minimum_credits", 0))
        self.max_edit.setValue(d.get("maximum_credits", 0))
        self.unique_edit.setValue(d.get("unique_course_limit", 1))
        times = d.get("times", {}) or {}
        for day, le in self.time_edits.items():
            vals = times.get(day, [])
            le.setText(vals[0] if vals else "")

        def _set_prefs(widget, pref_dict):
            if not pref_dict:
                widget.setPlainText("")
                return
            lines = [f"{k}:{v}" for k, v in pref_dict.items()]
            widget.setPlainText("\n".join(lines))

        _set_prefs(self.course_prefs, d.get("course_preferences", {}))
        _set_prefs(self.room_prefs, d.get("room_preferences", {}))
        _set_prefs(self.lab_prefs, d.get("lab_preferences", {}))

    def _lines(self, widget: QtWidgets.QPlainTextEdit) -> list[str]:
        text = widget.toPlainText().strip()
        if not text:
            return []
        return [line.strip() for line in text.splitlines() if line.strip()]

    def get_values(self) -> Dict[str, Any]:
        times = {d: (self.time_edits[d].text().strip() or "") for d in self.time_edits}
        return {
            "name": self.name_edit.text().strip(),
            "minimum_credits": int(self.min_edit.value()),
            "maximum_credits": int(self.max_edit.value()),
            "unique_course_limit": int(self.unique_edit.value()),
            "times": times,
            "course_pref_inputs": self._lines(self.course_prefs),
            "room_pref_inputs": self._lines(self.room_prefs),
            "lab_pref_inputs": self._lines(self.lab_prefs),
        }


class FacultyGUI(QtWidgets.QWidget):
    """Faculty GUI view. Handles UI and notifies FacultyController of actions.

    This view constructs a controller lazily to remain flexible about import
    ordering. The controller remains framework-agnostic and is easy to test.
    """

    def __init__(self, config: Dict[str, Any], loaded_path: Optional[str] = None, parent=None):
        super().__init__(parent)

        # Match main_gui sizing and title styling
        self.setWindowTitle("Faculty Manager")
        self.setMinimumWidth(800)
        self.setMinimumHeight(800)

        self.controller = FacultyController(config)

        self.loaded_path = loaded_path

        # Title label styled like main_gui
        title = QtWidgets.QLabel("Faculty Manager")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)

        self.list_widget = QtWidgets.QListWidget()

        # Buttons (styled to match main_gui)
        btn_style = "padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;"
        btn_font = QFont("Arial", 8)

        self.add_btn = QtWidgets.QPushButton("Add Faculty")
        self.add_btn.setFont(btn_font)
        self.add_btn.setStyleSheet(btn_style)

        self.edit_btn = QtWidgets.QPushButton("Edit Faculty")
        self.edit_btn.setFont(btn_font)
        self.edit_btn.setStyleSheet(btn_style)

        self.del_btn = QtWidgets.QPushButton("Delete Faculty")
        self.del_btn.setFont(btn_font)
        self.del_btn.setStyleSheet(btn_style)

        self.save_btn = QtWidgets.QPushButton("Save Config")
        self.save_btn.setFont(btn_font)
        self.save_btn.setStyleSheet(btn_style)

        # Layout
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.del_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(self.list_widget)
        layout.addLayout(btn_layout)

        # Signals: view handles button clicks, calls controller, then updates view
        self.add_btn.clicked.connect(self.add_faculty)
        self.edit_btn.clicked.connect(self.edit_faculty)
        self.del_btn.clicked.connect(self.delete_faculty)
        self.save_btn.clicked.connect(self.save_config)

        self.edit_btn.setEnabled(False)
        self.del_btn.setEnabled(False)
        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)

        self.refresh()

    def refresh(self):
        self.list_widget.clear()
        for f in self.controller.list_faculty():
            item = QtWidgets.QListWidgetItem(f.get("name", ""))
            item.setData(QtCore.Qt.UserRole, f)
            self.list_widget.addItem(item)
        self._on_selection_changed()

    def add_faculty(self):
        dlg = FacultyDialog(self)
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return
        raw = dlg.get_values()
        try:
            entry = self.controller.build_faculty_entry(
                name=raw["name"],
                minimum_credits=raw["minimum_credits"],
                maximum_credits=raw["maximum_credits"],
                unique_course_limit=raw["unique_course_limit"],
                times=raw["times"],
                course_pref_inputs=raw["course_pref_inputs"],
                room_pref_inputs=raw["room_pref_inputs"],
                lab_pref_inputs=raw["lab_pref_inputs"],
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Validation error", str(e))
            return

        added = self.controller.add_faculty(entry)
        if not added:
            QtWidgets.QMessageBox.information(self, "Exists", f"Faculty '{entry.get('name')}' already exists")
        self.refresh()

    def edit_faculty(self):
        item = self.list_widget.currentItem()
        if not item:
            QtWidgets.QMessageBox.information(self, "Select", "Select a faculty to edit")
            return
        existing = item.data(QtCore.Qt.UserRole) or {}
        old_name = existing.get("name")
        dlg = FacultyDialog(self, initial=existing)
        dlg.setWindowTitle("Edit Faculty")
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return
        raw = dlg.get_values()
        try:
            entry = self.controller.build_faculty_entry(
                name=raw["name"],
                minimum_credits=raw["minimum_credits"],
                maximum_credits=raw["maximum_credits"],
                unique_course_limit=raw["unique_course_limit"],
                times=raw["times"],
                course_pref_inputs=raw["course_pref_inputs"],
                room_pref_inputs=raw["room_pref_inputs"],
                lab_pref_inputs=raw["lab_pref_inputs"],
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Validation error", str(e))
            return

        success = self.controller.edit_faculty(old_name, entry)
        if not success:
            QtWidgets.QMessageBox.information(self, "Failed", "Edit failed (maybe new name exists)")
        self.refresh()

    def delete_faculty(self):
        item = self.list_widget.currentItem()
        if not item:
            QtWidgets.QMessageBox.information(self, "Select", "Select a faculty to delete")
            return
        name = item.text()
        confirm = QtWidgets.QMessageBox.question(self, "Confirm", f"Delete faculty '{name}'?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if confirm == QtWidgets.QMessageBox.Yes:
            self.controller.delete_faculty(name)
            self.refresh()

    def _on_selection_changed(self):
        item = self.list_widget.currentItem()
        has = bool(item)
        self.edit_btn.setEnabled(has)
        self.del_btn.setEnabled(has)

    def save_config(self):
        if self.loaded_path:
            path = Path(self.loaded_path)
        else:
            path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Config", "config.json", "JSON Files (*.json);;All Files (*)")
            if not path:
                return
            path = Path(path)

        try:
            # delegate saving to controller
            self.controller.save_config(str(path))
            if not self.loaded_path:
                self.loaded_path = str(path)
            QtWidgets.QMessageBox.information(self, "Saved", f"Config saved to {path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save config: {e}")


if __name__ == "__main__":
    import sys

    # Sample in-file configuration for standalone execution.
    sample_config = {
        "config": {
            "rooms": ["Room A", "Room B"],
            "courses": [{"course_id": "CS1", "room": ["Room A"]}],
            "labs": ["Linux"],
            "faculty": [{"name": "F1", "room_preferences": {"Room A": 1}}],
        }
    }
    app = QtWidgets.QApplication(sys.argv)
    w = FacultyGUI(sample_config, loaded_path=None)
    w.show()
    sys.exit(app.exec_())
