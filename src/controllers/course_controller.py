# src/controllers/course_controller.py

from typing import Dict, List
from src.models.course_model import Course, CourseManager


class CourseController:
    def __init__(self, manager: CourseManager) -> None:
        self.mgr = manager

    def load_courses(self, courses_data: list) -> None:
        """Load courses from data."""
        self.mgr.load_courses(courses_data)

    def list_courses(self) -> Dict[str, List[Course]]:
        """Get all courses."""
        return self.mgr.get_all_courses()

    def get_course_ids(self) -> List[str]:
        """Get all course IDs."""
        return self.mgr.get_course_ids()

    def get_course(self, course_id: str) -> List[Course]:
        """Get all instances of a specific course."""
        return self.mgr.get_course(course_id)

    def add_course(self, data: dict) -> None:
        """Add a new course."""
        course = Course(**data)
        self.mgr.add_course(course)

    def modify_course(self, course_id: str, index: int, data: dict) -> bool:
        """Modify an existing course."""
        new_course = Course(**data)
        return self.mgr.modify_course(course_id, index, new_course)

    def delete_course(self, course_id: str, index: int) -> bool:
        """Delete a course instance."""
        return self.mgr.delete_course(course_id, index)

    def save_to_file(self, config: dict, time_slots: dict, config_file: str) -> bool:
        """Save to JSON file (CLI)."""
        return self.mgr.save_config(config, time_slots, config_file)

    def save_to_combined_config(self, combined_config) -> bool:
        """Save to CombinedConfig (GUI)."""
        return self.mgr.save_with_combined_config(combined_config)

    def run(self, config: dict, config_file: str, time_slots: dict) -> dict:
        """Main controller loop."""
        from src.views.cli.course_view_cli import CourseView

        self.mgr.load_courses(config.get("courses", []))

        while True:
            CourseView.show_menu()
            choice = CourseView.get_menu_choice()

            if choice == "1":
                CourseView.display_courses(self)
            elif choice == "2":
                CourseView.add_course_interactive(self)
            elif choice == "3":
                CourseView.modify_course_interactive(self)
            elif choice == "4":
                CourseView.delete_course_interactive(self)
            elif choice == "5":
                if self.mgr.save_config(config, time_slots, config_file):
                    print(f"✅ Configuration saved successfully to {config_file}")
                    return config
                else:
                    print("❌ Failed to save configuration.")
                    return config
            elif choice == "6":
                print("Exiting without saving changes.")
                return config
            else:
                print("❌ Invalid choice. Please select 1-6.")
