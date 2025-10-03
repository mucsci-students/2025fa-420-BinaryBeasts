from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt  # Added for alignment and Qt namespace enums
from typing import Optional, List, Sequence, Any
from room import RoomManager  # Using direct module import; running script from src so 'src.' prefix breaks
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
    """Room management widget.

    Supports two construction modes:

    1. Legacy config dict mode (backward compatible):
        RoomGUI(config=<full_config_dict>, loaded_path=path)
       Expects a mapping with top-level key 'config' containing 'rooms', 'courses', 'faculty', etc.

    2. Adapter mode (new):
        RoomGUI(config=None, rooms=[...], course_configs=[CourseConfig, ...])
       Where rooms is a list of room names and course_configs is a sequence of CourseConfig-like
       objects (from the optional scheduler package) that expose a room attribute/field:
           - Tries attributes in order: 'room', 'rooms', 'room_list'.
           - Each attribute value should be a list[str] (or str which is coerced to a single-item list).

       The adapter mode internally builds a synthetic config dict for RoomManager while preserving
       references needed to push room edits back into the original course config objects.

    After any room change (add/edit/delete), adapter mode propagates updates back to the course
    config objects by mutating their discovered room attribute.

    Saving:
        In adapter mode, save_config will serialize a minimal JSON object:
            {"rooms": [...], "courses": [{"rooms": [...]}, ...]}
        (Using key 'rooms' irrespective of the original attribute name for uniformity.)
        In legacy mode, behavior is unchanged (attempt CombinedConfig validation then dump full dict).
    """

    def __init__(self,
                 config: Optional[dict] = None,
                 loaded_path: Optional[str] = None,
                 parent=None,
                 rooms: Optional[Sequence[str]] = None,
                 course_configs: Optional[Sequence[Any]] = None):
        super().__init__(parent)
        self.setWindowTitle("Room Manager")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.loaded_path = loaded_path

        # Determine mode
        self._adapter_mode = False
        self._course_adapter_records: List[dict] = []  # Each: {'obj': obj, 'attr': attr_name, 'rooms': list_ref}

        if config is not None:
            # Legacy direct config mode
            self.manager = RoomManager(config)
        else:
            # Adapter mode requires rooms list (can be empty) and optional course configs
            if rooms is None:
                raise ValueError("Either a legacy config dict or a rooms list must be provided.")
            self._adapter_mode = True
            synthetic_config = {"config": {"rooms": list(rooms), "courses": []}}
            # Build synthetic courses list capturing current room assignments to let RoomManager
            # adjust them on rename/delete. We'll maintain a mapping back to original objects.
            if course_configs:
                for c in course_configs:
                    attr_name = None
                    for candidate in ("room", "rooms", "room_list"):
                        if hasattr(c, candidate):
                            attr_name = candidate
                            break
                    # Extract rooms value
                    if attr_name is not None:
                        value = getattr(c, attr_name)
                        if isinstance(value, str):
                            value_list = [value]
                        elif isinstance(value, (list, tuple)):
                            value_list = [v for v in value if isinstance(v, str)]
                        else:
                            value_list = []
                    else:
                        value_list = []
                    course_entry = {"room": list(value_list)}  # structure compatible with RoomManager expectations
                    synthetic_config["config"]["courses"].append(course_entry)
                    self._course_adapter_records.append({
                        "obj": c,
                        "attr": attr_name,
                        "rooms": course_entry["room"],  # keep reference for synchronization
                    })
            self.manager = RoomManager(synthetic_config)

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
            self._adapter_sync_back()

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
            if success:
                self._adapter_sync_back(old_name=old, new_name=new)

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
            self._adapter_sync_back(deleted=rm)

    def _on_selection_changed(self):
        """Enable or disable edit/delete buttons based on selection."""
        item = self.list_widget.currentItem()
        has = bool(item)
        self.edit_btn.setEnabled(has)
        self.del_btn.setEnabled(has)

    def save_config(self):
        """Save current data.

        Legacy mode: behaves as before (attempt CombinedConfig validation + full config JSON).
        Adapter mode: writes a minimal JSON with updated rooms and course room assignments.
        """
        # If we have a loaded file path, overwrite it directly. Otherwise ask the user.
        if self.loaded_path:
            path = self.loaded_path
        else:
            options = QFileDialog.Options()
            path, _ = QFileDialog.getSaveFileName(self, "Save Config", "config.json", "JSON Files (*.json);;All Files (*)", options=options)
            if not path:
                return
        try:
            if self._adapter_mode:
                # Build minimal export
                export_courses = []
                for rec in self._course_adapter_records:
                    export_courses.append({"rooms": list(rec["rooms"])})
                data = {"rooms": self.manager.get_rooms(), "courses": export_courses}
            else:
                # The RoomManager stores the config dict by reference. Prefer to validate
                # and serialize using the scheduler package's CombinedConfig if available
                # (keeps Pydantic serialization rules), otherwise fall back to a plain JSON dump.
                try:
                    from scheduler.config import CombinedConfig  # type: ignore
                    combined = CombinedConfig.model_validate(self.manager.config)
                    data = combined.model_dump()
                except Exception:
                    data = self.manager.config

            # Write JSON to disk using standard library for portability
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            # If we saved to a chosen path and we didn't previously have a loaded_path,
            # remember this path as the loaded file for future saves.
            if not self.loaded_path:
                self.loaded_path = path
            if not self._adapter_mode:
                # Optional post-save validation using scheduler models (if available)
                _try_validate_with_scheduler(self.manager.config, parent=self)
            QtWidgets.QMessageBox.information(self, "Saved", f"Config saved to {path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save config: {e}")

    # ---------------- Adapter sync helpers -----------------
    def _adapter_sync_back(self, old_name: Optional[str] = None, new_name: Optional[str] = None, deleted: Optional[str] = None):
        """If in adapter mode, propagate current room assignments back to original course objects.

        Args:
            old_name: If a rename occurred, the prior room name.
            new_name: New name after rename.
            deleted: If a deletion occurred, the removed room name.
        """
        if not self._adapter_mode:
            return
        current_rooms = set(self.manager.get_rooms())
        # Update each course record's room list to remove deleted rooms and ensure rename consistency
        for rec in self._course_adapter_records:
            attr = rec["attr"]
            if attr is None:
                continue  # no attribute discovered
            obj = rec["obj"]
            room_list = rec["rooms"]  # already updated by RoomManager if rename; but need prune deletes
            # Prune deleted / removed rooms not in current list
            updated_list = [r for r in room_list if r in current_rooms]
            # Commit list back to object attribute (preserve type list)
            setattr(obj, attr, list(updated_list))
        # Additional rename handling if RoomManager didn't propagate (adapter synthetic courses might not exist)
        if old_name and new_name and old_name not in current_rooms and new_name in current_rooms:
            for rec in self._course_adapter_records:
                attr = rec["attr"]
                if attr is None:
                    continue
                obj = rec["obj"]
                values = getattr(obj, attr)
                if isinstance(values, list):
                    setattr(obj, attr, [new_name if v == old_name else v for v in values])
                elif isinstance(values, str) and values == old_name:
                    setattr(obj, attr, new_name)

    # Public helper to retrieve current rooms (useful for adapter mode callers)
    def get_current_rooms(self) -> List[str]:
        return self.manager.get_rooms()


def create_room_window(config: Optional[dict] = None,
                       loaded_path: Optional[str] = None,
                       parent=None,
                       rooms: Optional[Sequence[str]] = None,
                       course_configs: Optional[Sequence[Any]] = None) -> Optional[RoomGUI]:  # type: ignore[name-defined]
    """Factory/helper to build a RoomGUI safely.

    Supports both legacy (config dict) and new adapter (rooms + course_configs) usage.

    Examples:
        # Legacy
        w = create_room_window(config=my_full_config)

        # Adapter from scheduler CourseConfig objects
        w = create_room_window(rooms=["R1","R2"], course_configs=[course1, course2])

    Args:
        config: Legacy full configuration dictionary with 'config' key.
        loaded_path: Original file path (enables overwrite on save).
        parent: Optional parent QWidget for modality/ownership.
        rooms: List/sequence of room names when using adapter mode (config must be None).
        course_configs: Sequence of CourseConfig-like objects (optional) for adapter mode.

    Returns:
        RoomGUI instance or None if construction failed / invalid input.
    """
    try:
        if config is None and rooms is None:
            msg = "No configuration or rooms provided. Provide a config dict or rooms list."
            if parent is not None:
                QtWidgets.QMessageBox.warning(parent, "Room Manager", msg)
            else:
                print(f"[RoomGUI] {msg}")
            return None

        if config is not None and rooms is not None:
            msg = "Provide either config or rooms (adapter mode), not both."
            if parent is not None:
                QtWidgets.QMessageBox.warning(parent, "Room Manager", msg)
            else:
                print(f"[RoomGUI] {msg}")
            return None

        if config is not None:
            # Optional validation against scheduler's Pydantic models if available
            _try_validate_with_scheduler(config, parent)
            widget = RoomGUI(config=config, loaded_path=loaded_path, parent=parent)
        else:
            # adapter mode
            widget = RoomGUI(config=None, loaded_path=loaded_path, parent=parent, rooms=rooms, course_configs=course_configs)
        return widget
    except Exception as e:  # pragma: no cover - defensive GUI path
        try:
            if parent is not None:
                QtWidgets.QMessageBox.critical(parent, "Room GUI Error", f"Failed to create Room window:\n{e}")
            else:
                print(f"[RoomGUI] Error constructing RoomGUI: {e}")
        finally:
            return None


if __name__ == "__main__":
    import sys

    # Legacy example
    sample_config = {
        "config": {
            "rooms": ["Room A", "Room B", "Room C"],
            "courses": [{"course_id": "CS1", "room": ["Room A"]}],
            "faculty": [{"name": "F1", "room_preferences": {"Room A": 1}}],
        }
    }

    class MockCourse:
        def __init__(self, name, room):
            self.name = name
            self.room = [room] if isinstance(room, str) else list(room)

        def __repr__(self):
            return f"MockCourse(name={self.name}, room={self.room})"

    course_objs = [MockCourse("CS1", ["Room A"]), MockCourse("CS2", ["Room B", "Room C"])]

    app = QtWidgets.QApplication(sys.argv)
    # Toggle between legacy and adapter mode for manual test
    legacy = False
    if legacy:
        w = create_room_window(sample_config)
    else:
        w = create_room_window(rooms=["Room A", "Room B", "Room C"], course_configs=course_objs)
    if w:
        w.show()
        app.exec_()
        print("Final rooms:", w.get_current_rooms())
        print("Course objects after edits:", course_objs)


def _try_validate_with_scheduler(raw_config: dict, parent=None) -> bool:
    """Attempt to validate the provided raw_config with scheduler.CombinedConfig if installed.

    This uses the documented Scheduler model structure (SchedulerConfig inside CombinedConfig):
      CombinedConfig(config=SchedulerConfig(...), time_slot_config=TimeSlotConfig(...), ...)

    We only care here about the 'config' (rooms/courses/faculty/labs). If validation fails,
    we show a warning but still allow the GUI to open so the user can fix issues.

    Returns True if validation succeeded (or scheduler not present), False if validation failed.
    """
    try:
        from scheduler.config import CombinedConfig, SchedulerConfig  # type: ignore
        # Extract scheduler section; tolerate both wrapped {'config': {...}} and direct schema.
        if 'config' in raw_config and isinstance(raw_config['config'], dict) and any(k in raw_config['config'] for k in ('rooms','courses','faculty','labs')):
            sched_section = raw_config['config']
        else:
            sched_section = raw_config  # assume already flattened

        try:
            # Build minimal CombinedConfig with only required 'config' part; supply placeholders for others if needed.
            # We ignore time_slot_config etc. to keep this lightweight. If constructor requires them, we adapt.
            combined_kwargs = {'config': SchedulerConfig(**sched_section)}
            # Some versions may expect time_slot_config, limit, optimizer_flags; we attempt graceful fallback.
            try:
                CombinedConfig(**combined_kwargs)  # type: ignore[arg-type]
            except TypeError:
                # Provide minimal placeholders if required
                if 'time_slot_config' not in combined_kwargs:
                    combined_kwargs['time_slot_config'] = {'times': {}, 'classes': []}
                if 'limit' not in combined_kwargs:
                    combined_kwargs['limit'] = 1
                if 'optimizer_flags' not in combined_kwargs:
                    combined_kwargs['optimizer_flags'] = []
                CombinedConfig(**combined_kwargs)  # Second attempt
            return True
        except Exception as e:  # Validation failed
            warn_msg = f"Config validation (scheduler) failed: {e}"
            if parent is not None:
                QtWidgets.QMessageBox.warning(parent, "Room Config Validation", warn_msg)
            else:
                print(f"[RoomGUI] {warn_msg}")
            return False
    except ImportError:
        # Scheduler package not installed; silently succeed
        return True
    except Exception as e:  # Unexpected issue in validation path
        print(f"[RoomGUI] Unexpected validation error: {e}")
        return False
