# src/controllers/faculty_controller.py

from typing import Dict, List, Optional
from src.models.faculty_model import Faculty, FacultyManager


class FacultyController:
    """Controller for faculty management - bridges view and model layers."""

    def __init__(self, manager: FacultyManager) -> None:
        self.mgr = manager

    def load_faculty(self, faculty_data: list) -> None:
        """Load faculty from data."""
        self.mgr.load_faculty(faculty_data)

    def list_faculty(self) -> Dict[str, Faculty]:
        """Get all faculty."""
        return self.mgr.get_all_faculty()

    def get_faculty_names(self) -> List[str]:
        """Get all faculty names."""
        return self.mgr.get_faculty_names()

    def get_faculty(self, name: str) -> Optional[Faculty]:
        """Get a specific faculty member."""
        return self.mgr.get_faculty(name)

    def faculty_exists(self, name: str) -> bool:
        """Check if faculty exists."""
        return self.mgr.faculty_exists(name)

    def add_faculty(self, data: dict) -> bool:
        """Add a new faculty member."""
        faculty = Faculty(**data)
        return self.mgr.add_faculty(faculty)

    def modify_faculty(self, name: str, data: dict) -> bool:
        """Modify an existing faculty member."""
        new_faculty = Faculty(**data)
        return self.mgr.modify_faculty(name, new_faculty)

    def delete_faculty(self, name: str) -> bool:
        """Delete a faculty member."""
        return self.mgr.delete_faculty(name)

    def save_to_file(self, config: dict, time_slots: dict, config_file: str) -> bool:
        """Save to JSON file (CLI)."""
        return self.mgr.save_config(config, time_slots, config_file)

    def save_to_combined_config(self, combined_config) -> bool:
        """Save to CombinedConfig (GUI)."""
        return self.mgr.save_with_combined_config(combined_config)
