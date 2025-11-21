# src/controllers/room_controller.py

from src.models.room_model import RoomManager
from typing import List, Dict, Optional
from src.undo_manager import SnapshotUndoManager


class RoomController:
    """Controller layer for room management - bridges view and model."""

    def __init__(self, manager: RoomManager, undo_manager: Optional[SnapshotUndoManager] = None) -> None:
        """
        Initialize RoomController.

        Args:
            manager: RoomManager instance to control
        """
        self.mgr = manager
        self.undo_manager = undo_manager

    def _record_change(self) -> None:
        """Helper: record a snapshot after a successful change."""
        if self.undo_manager is not None:
            self.undo_manager.record_change()

    def add_room(self, room_name: str) -> bool:
        """
        Add a new room.

        Args:
            room_name: Name of the room to add

        Returns:
            True if room was added, False if it already exists
        """
        try:
            ok = self.mgr.add_room(room_name)
            if ok:
                self._record_change()
            return ok
        except ValueError as e:
            raise e

    def delete_room(self, room_name: str) -> bool:
        """
        Delete a room.

        Args:
            room_name: Name of the room to delete

        Returns:
            True if room was deleted, False if it doesn't exist
        """
        ok = self.mgr.delete_room(room_name)
        if ok:
            self._record_change()
        return ok

    def edit_room(self, old_name: str, new_name: str) -> bool:
        """
        Rename a room.

        Args:
            old_name: Current name of the room
            new_name: New name for the room

        Returns:
            True if room was renamed, False if old_name doesn't exist or new_name already exists
        """
        try:
            ok = self.mgr.edit_room(old_name, new_name)
            if ok:
                self._record_change()
            return ok
        except ValueError as e:
            raise e

    def undo(self) -> bool:
        """Undo the last room change."""
        if self.undo_manager is None:
            return False
        return self.undo_manager.undo()

    def redo(self) -> bool:
        """Redo the last undone room change."""
        if self.undo_manager is None:
            return False
        return self.undo_manager.redo()

    def get_rooms(self) -> List[str]:
        """
        Get all rooms.

        Returns:
            List of room names
        """
        return self.mgr.get_rooms()

    def room_exists(self, room_name: str) -> bool:
        """
        Check if a room exists.

        Args:
            room_name: Name of the room to check

        Returns:
            True if room exists, False otherwise
        """
        return self.mgr.room_exists(room_name)

    def update_room_references(
        self, old_name: str, new_name: str, courses_dict: Dict, faculty_dict: Dict
    ) -> None:
        """
        Update room references in courses and faculty when a room is renamed.

        Args:
            old_name: Old room name
            new_name: New room name
            courses_dict: Dictionary of courses to update
            faculty_dict: Dictionary of faculty to update
        """
        self.mgr.update_room_references(old_name, new_name, courses_dict, faculty_dict)

    def remove_room_references(
        self, room_name: str, courses_dict: Dict, faculty_dict: Dict
    ) -> None:
        """
        Remove room references from courses and faculty when a room is deleted.

        Args:
            room_name: Room name to remove
            courses_dict: Dictionary of courses to update
            faculty_dict: Dictionary of faculty to update
        """
        self.mgr.remove_room_references(room_name, courses_dict, faculty_dict)

    def save_to_combined_config(self, combined_config) -> bool:
        """
        Save rooms back to CombinedConfig.

        Args:
            combined_config: CombinedConfig object to update

        Returns:
            True if save was successful
        """
        try:
            with combined_config.edit_mode() as editable_config:
                editable_config.config.rooms = self.mgr.get_rooms()
            return True
        except Exception:
            return False
