# src/models/room_model.py

from typing import List, Dict
from scheduler.config import CombinedConfig


class RoomManager:
    """Manages room data with support for both dict-based and CombinedConfig-based workflows."""

    def __init__(self, config: CombinedConfig = None):
        """
        Initialize RoomManager.

        Args:
            config: Optional CombinedConfig object. If provided, loads rooms from it.
        """
        self.rooms: List[str] = []
        if config:
            self.load_rooms(config)

    def load_rooms(self, config: CombinedConfig) -> None:
        """
        Load rooms from a CombinedConfig object.

        Args:
            config: CombinedConfig object containing room data
        """
        # (config.config.rooms) and (config.rooms)
        if hasattr(config, "config") and hasattr(config.config, "rooms"):
            self.rooms = list(config.config.rooms) if config.config.rooms else []
        elif hasattr(config, "rooms"):
            self.rooms = list(config.rooms) if config.rooms else []
        else:
            self.rooms = []

    def add_room(self, room_name: str) -> bool:
        """
        Add a new room.

        Args:
            room_name: Name of the room to add

        Returns:
            True if room was added, False if it already exists
        """
        if not room_name:
            raise ValueError("Room name cannot be empty")

        if room_name in self.rooms:
            return False

        self.rooms.append(room_name)
        return True

    def delete_room(self, room_name: str) -> bool:
        """
        Delete a room.

        Args:
            room_name: Name of the room to delete

        Returns:
            True if room was deleted, False if it doesn't exist
        """
        if room_name not in self.rooms:
            return False

        self.rooms.remove(room_name)
        return True

    def edit_room(self, old_name: str, new_name: str) -> bool:
        """
        Rename a room.

        Args:
            old_name: Current name of the room
            new_name: New name for the room

        Returns:
            True if room was renamed, False if old_name doesn't exist or new_name already exists
        """
        if not new_name:
            raise ValueError("New room name cannot be empty")

        if old_name not in self.rooms:
            return False

        if new_name in self.rooms:
            return False

        index = self.rooms.index(old_name)
        self.rooms[index] = new_name
        return True

    def get_rooms(self) -> List[str]:
        """
        Get all rooms.

        Returns:
            List of room names
        """
        return self.rooms.copy()

    def room_exists(self, room_name: str) -> bool:
        """
        Check if a room exists.

        Args:
            room_name: Name of the room to check

        Returns:
            True if room exists, False otherwise
        """
        return room_name in self.rooms

    def set_rooms(self, rooms: List[str]) -> None:
        """
        Replace all rooms with a new list.

        Args:
            rooms: New list of room names
        """
        self.rooms = list(rooms)

    def to_dict(self) -> Dict:
        """
        Convert rooms to a dictionary format compatible with SchedulerConfig.

        Returns:
            Dictionary with 'rooms' key containing list of room names
        """
        return {"rooms": self.rooms}

    def save_config(self, config: Dict) -> Dict:
        """
        Update a configuration dictionary with current room data.

        Args:
            config: Dictionary configuration to update

        Returns:
            Updated configuration dictionary
        """
        config["rooms"] = self.rooms
        return config

    def save_with_combined_config(self, config: CombinedConfig) -> CombinedConfig:
        """
        Update a CombinedConfig object with current room data.

        Args:
            config: CombinedConfig object to update

        Returns:
            Updated CombinedConfig object
        """
        # Update rooms in the config
        config.rooms = self.rooms.copy()
        return config

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
        # Update course room assignments
        for course_id, instances in courses_dict.items():
            for course in instances:
                if hasattr(course, "room") and old_name in course.room:
                    course.room = [
                        new_name if r == old_name else r for r in course.room
                    ]

        # Update faculty room preferences
        for name, faculty in faculty_dict.items():
            if (
                hasattr(faculty, "room_preferences")
                and old_name in faculty.room_preferences
            ):
                preference = faculty.room_preferences[old_name]
                del faculty.room_preferences[old_name]
                faculty.room_preferences[new_name] = preference

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
        # Remove from course room assignments
        for course_id, instances in courses_dict.items():
            for course in instances:
                if hasattr(course, "room") and room_name in course.room:
                    course.room = [r for r in course.room if r != room_name]

        # Remove from faculty room preferences
        for name, faculty in faculty_dict.items():
            if (
                hasattr(faculty, "room_preferences")
                and room_name in faculty.room_preferences
            ):
                del faculty.room_preferences[room_name]
