from typing import Dict, Any, List, Optional

from scheduler.config import CombinedConfig
from src.managers.faculty_manager import FacultyManager


class FacultyController:
    """Thin controller that delegates to FacultyManager and handles errors.

    Methods return Python-native results where sensible (lists/dicts/bools).
    For mutating operations that previously returned None on success, this
    controller returns None on success and an Exception (or error) on failure
    to match the pattern used by CourseController.
    """

    def __init__(self, combined_config: CombinedConfig):
        self.combined_config = combined_config
        self.manager = FacultyManager(combined_config)
        self.view = None #set later to avoid circular import

    #@set as object instead of FacultyView to avoid circular import    
    def set_view(self, view: object) -> None:
        self.view = view

    def get_faculty(self) -> List[Dict[str, Any]]:
        try:
            return self.manager.get_faculty()
        except Exception as e:
            print(f"Error getting faculty: {e}")
            return []

    def add_faculty(self, faculty: Dict[str, Any]) -> Optional[Exception]:
        try:
            ok = self.manager.add_faculty(faculty)
            if ok:
                return None
            return Exception("Faculty already exists")
        except Exception as e:
            print(f"Error adding faculty: {e}")
            return e

    def delete_faculty(self, name: str) -> bool:
        try:
            return self.manager.delete_faculty(name)
        except Exception as e:
            print(f"Error deleting faculty: {e}")
            return False

    def edit_faculty(self, name: str, new_data: Dict[str, Any]) -> bool:
        try:
            return self.manager.edit_faculty(name, new_data)
        except Exception as e:
            print(f"Error editing faculty: {e}")
            return False

    def set_faculty(self, new_faculty: List[Dict[str, Any]]):
        try:
            return self.manager.set_faculty(new_faculty)
        except Exception as e:
            print(f"Error setting faculty list: {e}")
            return e

    def faculty_management_menu(self) -> Dict[str, Any]:
        try:
            print("Entering faculty management menu...")
            return self.view.faculty_management_menu(self.combined_config)
        except Exception as e:
            print(f"Error in faculty management menu: {e}")
            return e