# src/controllers/lab_controller.py

from src.models.lab_model import LabManager
from typing import List, Dict, Optional
from src.undo_manager import SnapshotUndoManager


class LabController:
    """Controller layer for lab management - bridges view and model."""

    def __init__(self, manager: LabManager, undo_manager: Optional[SnapshotUndoManager] = None) -> None:
        """
        Initialize LabController.

        Args:
            manager: LabManager instance to control
        """
        self.mgr = manager
        self.undo_manager = undo_manager

    def _record_change(self) -> None:
        """Helper: record a snapshot after a successful change."""
        if self.undo_manager is not None:
            self.undo_manager.record_change()

    def add_lab(self, lab_name: str) -> bool:
        """
        Add a new lab.

        Args:
            lab_name: Name of the lab to add

        Returns:
            True if lab was added, False if it already exists
        """
        ok = self.mgr.add_lab(lab_name)
        if ok:
            self._record_change()
        return ok

    def delete_lab(self, lab_name: str) -> bool:
        """
        Delete a lab.

        Args:
            lab_name: Name of the lab to delete

        Returns:
            True if lab was deleted, False if it doesn't exist
        """
        ok = self.mgr.delete_lab(lab_name)
        if ok:
            self._record_change()
        return ok

    def edit_lab(self, old_name: str, new_name: str) -> bool:
        """
        Rename a lab.

        Args:
            old_name: Current name of the lab
            new_name: New name for the lab

        Returns:
            True if lab was renamed, False if old_name doesn't exist or new_name already exists
        """
        ok = self.mgr.edit_lab(old_name, new_name)
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

    def get_labs(self) -> List[str]:
        """
        Get all labs.

        Returns:
            List of lab names
        """
        return self.mgr.get_labs()

    def lab_exists(self, lab_name: str) -> bool:
        """
        Check if a lab exists.

        Args:
            lab_name: Name of the lab to check

        Returns:
            True if lab exists, False otherwise
        """
        return self.mgr.lab_exists(lab_name)

    def update_lab_references(
        self, old_name: str, new_name: str, courses_dict: Dict, faculty_dict: Dict
    ) -> None:
        """
        Update lab references in courses and faculty when a lab is renamed.

        Args:
            old_name: Old lab name
            new_name: New lab name
            courses_dict: Dictionary of courses to update
            faculty_dict: Dictionary of faculty to update
        """
        self.mgr.update_lab_references(old_name, new_name, courses_dict, faculty_dict)

    def remove_lab_references(
        self, lab_name: str, courses_dict: Dict, faculty_dict: Dict
    ) -> None:
        """
        Remove lab references from courses and faculty when a lab is deleted.

        Args:
            lab_name: Lab name to remove
            courses_dict: Dictionary of courses to update
            faculty_dict: Dictionary of faculty to update
        """
        self.mgr.remove_lab_references(lab_name, courses_dict, faculty_dict)

    def save_to_combined_config(self, combined_config) -> bool:
        """
        Save labs back to CombinedConfig.

        Args:
            combined_config: CombinedConfig object to update

        Returns:
            True if save was successful
        """
        try:
            with combined_config.edit_mode() as editable_config:
                editable_config.config.labs = self.mgr.get_labs()
            return True
        except Exception:
            return False
