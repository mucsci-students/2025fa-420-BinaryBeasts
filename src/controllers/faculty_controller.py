# src/controllers/faculty_controller.py

from typing import Dict, List, Optional
from src.models.faculty_model import Faculty, FacultyManager
from src.undo_manager import SnapshotUndoManager


class FacultyController:
    """Controller for faculty management - bridges view and model layers."""

    def __init__(self, manager: FacultyManager, undo_manager: Optional[SnapshotUndoManager] = None) -> None:
        self.mgr = manager
        self.undo_manager = undo_manager

    def _record_change(self) -> None:
        """Helper: record a snapshot after a successful change."""
        if self.undo_manager is not None:
            self.undo_manager.record_change()

    def load_faculty(self, faculty_data: list) -> None:
        """Load faculty from data."""
        self.mgr.load_faculty(faculty_data)

    def list_faculty(self) -> Dict[str, Faculty]:
        """Get all faculty."""
        return self.mgr.get_all_faculty()

    def get_faculty_names(self) -> List[str]:
        """Get all faculty names."""
        return self.mgr.get_faculty_names()

    def get_faculty(self, name: str) -> Faculty:
        """Get a specific faculty member."""
        return self.mgr.get_faculty(name)

    def faculty_exists(self, name: str) -> bool:
        """Check if faculty exists."""
        return self.mgr.faculty_exists(name)

    def add_faculty(self, data: dict) -> bool:
        """Add a new faculty member."""
        faculty = Faculty(**data)
        ok = self.mgr.add_faculty(faculty)
        if ok:
            self._record_change()
        return ok

    def modify_faculty(self, name: str, data: dict) -> bool:
        """Modify an existing faculty member."""
        new_faculty = Faculty(**data)
        ok = self.mgr.modify_faculty(name, new_faculty)
        if ok:
            self._record_change()
        return ok

    def delete_faculty(self, name: str) -> bool:
        """Delete a faculty member."""
        ok = self.mgr.delete_faculty(name)
        if ok:
            self._record_change()
        return ok

    def undo(self) -> bool:
        """Undo the last faculty change."""
        if self.undo_manager is None:
            return False
        return self.undo_manager.undo()

    def redo(self) -> bool:
        """Redo the last undone faculty change."""
        if self.undo_manager is None:
            return False
        return self.undo_manager.redo()

    def save_to_file(self, config: dict, time_slots: dict, config_file: str) -> bool:
        """Save to JSON file (CLI)."""
        return self.mgr.save_config(config, time_slots, config_file)

    def save_to_combined_config(self, combined_config) -> bool:
        """Save to CombinedConfig (GUI)."""
        return self.mgr.save_with_combined_config(combined_config)
