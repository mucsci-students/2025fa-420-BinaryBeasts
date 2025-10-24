# src/models/faculty_model.py

import json
from typing import Dict, List, Optional


class Faculty:
    """
    Represents an individual faculty member.
    """

    def __init__(
        self,
        name: str,
        minimum_credits: int = 0,
        maximum_credits: int = 9,
        unique_course_limit: int = 1,
        times: Dict[str, List[str]] = {},
        course_preferences: Dict[str, int] = {},
        room_preferences: Dict[str, int] = {},
        lab_preferences: Dict[str, int] = {},
    ):
        self.name = name
        self.minimum_credits = minimum_credits
        self.maximum_credits = maximum_credits
        self.unique_course_limit = unique_course_limit
        self.times = times if times is not None else {}
        self.course_preferences = (
            course_preferences if course_preferences is not None else {}
        )
        self.room_preferences = room_preferences if room_preferences is not None else {}
        self.lab_preferences = lab_preferences if lab_preferences is not None else {}

        if not self.name:
            raise ValueError("Faculty name cannot be empty")
        if self.minimum_credits < 0:
            raise ValueError("Minimum credits must be non-negative")
        if self.maximum_credits < self.minimum_credits:
            raise ValueError("Maximum credits cannot be less than minimum credits")
        if self.unique_course_limit < 1:
            raise ValueError("Unique course limit must be at least 1")


class FacultyManager:
    """
    Manages faculty members for the scheduling system.
    """

    def __init__(self, faculty_list: Optional[List[Faculty]] = None) -> None:
        self.faculty: Dict[str, Faculty] = {}
        if faculty_list:
            for fac in faculty_list:
                self.faculty[fac.name] = fac

    def load_faculty(self, faculty_data: List[Dict]) -> None:
        """
        Load faculty data from a list of dictionaries.
        """
        for fd in faculty_data:
            try:
                faculty = Faculty(
                    name=str(fd.get("name", "")).strip(),
                    minimum_credits=int(fd.get("minimum_credits", 0)),
                    maximum_credits=int(fd.get("maximum_credits", 9)),
                    unique_course_limit=int(fd.get("unique_course_limit", 1)),
                    times=dict(fd.get("times", {})),
                    course_preferences=dict(fd.get("course_preferences", {})),
                    room_preferences=dict(fd.get("room_preferences", {})),
                    lab_preferences=dict(fd.get("lab_preferences", {})),
                )
                self.add_faculty(faculty)
            except (ValueError, TypeError) as e:
                print(f"Warning: Invalid faculty data - {e}")

    def add_faculty(self, faculty: Faculty) -> bool:
        """
        Add a faculty member to the manager.
        Returns False if faculty with same name already exists.

        :param faculty: Faculty object to add
        :return: True if added, False if already exists
        """
        if faculty.name in self.faculty:
            return False
        self.faculty[faculty.name] = faculty
        return True

    def delete_faculty(self, name: str) -> bool:
        """
        Delete a faculty member by name.

        :param name: Name of faculty to delete
        :return: True if deleted, False if not found
        """
        if name not in self.faculty:
            return False
        del self.faculty[name]
        return True

    def get_faculty(self, name: str) -> Optional[Faculty]:
        """
        Get a specific faculty member by name.

        :param name: Faculty name
        :return: Faculty object or None if not found
        """
        return self.faculty.get(name)

    def get_all_faculty(self) -> Dict[str, Faculty]:
        """
        Get all faculty members.

        :return: Dictionary of faculty name -> Faculty object
        """
        return self.faculty.copy()

    def get_faculty_names(self) -> List[str]:
        """
        Get list of all faculty names.

        :return: List of faculty names
        """
        return list(self.faculty.keys())

    def faculty_exists(self, name: str) -> bool:
        """
        Check if a faculty member exists.

        :param name: Faculty name
        :return: True if exists, False otherwise
        """
        return name in self.faculty

    def modify_faculty(self, name: str, new_faculty: Faculty) -> bool:
        """
        Modify an existing faculty member.

        :param name: Current name of faculty
        :param new_faculty: New Faculty object
        :return: True if modified, False if not found or new name exists
        """
        if name not in self.faculty:
            return False

        # If renaming, check that new name doesn't exist
        if new_faculty.name != name and new_faculty.name in self.faculty:
            return False

        # Delete old entry
        del self.faculty[name]
        # Add new entry
        self.faculty[new_faculty.name] = new_faculty
        return True

    def to_dict(self) -> List[Dict]:
        """Convert faculty to dictionary format for saving."""
        faculty_list = []
        for faculty in self.faculty.values():
            faculty_list.append(
                {
                    "name": faculty.name,
                    "minimum_credits": faculty.minimum_credits,
                    "maximum_credits": faculty.maximum_credits,
                    "unique_course_limit": faculty.unique_course_limit,
                    "times": faculty.times,
                    "course_preferences": faculty.course_preferences,
                    "room_preferences": faculty.room_preferences,
                    "lab_preferences": faculty.lab_preferences,
                }
            )
        return faculty_list

    def save_config(self, config: dict, time_slots: dict, config_file: str) -> bool:
        """Save configuration to file (for CLI)."""
        try:
            config["faculty"] = self.to_dict()
            full_config = {"config": config, "time_slot_config": time_slots}
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(full_config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def save_with_combined_config(self, combined_config) -> bool:
        """Save faculty to CombinedConfig (for GUI)."""
        try:
            from scheduler.config import FacultyConfig

            with combined_config.edit_mode() as editable_config:
                # Clear existing faculty
                editable_config.config.faculty.clear()

                # Add all faculty from this manager
                for faculty in self.faculty.values():
                    new_faculty = FacultyConfig(
                        name=faculty.name,
                        minimum_credits=faculty.minimum_credits,
                        maximum_credits=faculty.maximum_credits,
                        unique_course_limit=faculty.unique_course_limit,
                        times=faculty.times,
                        course_preferences=faculty.course_preferences,
                        room_preferences=faculty.room_preferences,
                        lab_preferences=faculty.lab_preferences,
                    )
                    editable_config.config.faculty.append(new_faculty)
            return True
        except Exception as e:
            print(f"Error saving: {e}")
            return False
