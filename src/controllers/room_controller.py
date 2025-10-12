# src/controllers/room_controller.py

from src.models.room_model import RoomManager
from typing import List, Dict


class RoomController:
    """Controller layer for room management - bridges view and model."""

    def __init__(self, manager: RoomManager) -> None:
        """
        Initialize RoomController.

        Args:
            manager: RoomManager instance to control
        """
        self.mgr = manager

    def add_room(self, room_name: str) -> bool:
        """
        Add a new room.

        Args:
            room_name: Name of the room to add

        Returns:
            True if room was added, False if it already exists
        """
        try:
            return self.mgr.add_room(room_name)
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
        return self.mgr.delete_room(room_name)

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
            return self.mgr.edit_room(old_name, new_name)
        except ValueError as e:
            raise e

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

    def update_room_references(self, old_name: str, new_name: str,
                               courses_dict: Dict, faculty_dict: Dict) -> None:
        """
        Update room references in courses and faculty when a room is renamed.

        Args:
            old_name: Old room name
            new_name: New room name
            courses_dict: Dictionary of courses to update
            faculty_dict: Dictionary of faculty to update
        """
        self.mgr.update_room_references(old_name, new_name, courses_dict, faculty_dict)

    def remove_room_references(self, room_name: str,
                               courses_dict: Dict, faculty_dict: Dict) -> None:
        """
        Remove room references from courses and faculty when a room is deleted.

        Args:
            room_name: Room name to remove
            courses_dict: Dictionary of courses to update
            faculty_dict: Dictionary of faculty to update
        """
        self.mgr.remove_room_references(room_name, courses_dict, faculty_dict)