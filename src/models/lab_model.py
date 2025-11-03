# src/models/lab_model.py

from typing import List, Dict
from scheduler.config import CombinedConfig
from src.observer_pattern import Observable, EventType, EventData


class LabManager(Observable):
    """
    Lab Manager with Observer pattern support.
    
    Manages lab data and notifies observers when labs are added, updated, or removed.
    """

    def __init__(self, config):
        """
        Initialize LabManager with Observer pattern support.

        Args:
            config: Optional CombinedConfig object. If provided, loads labs from it.
        """
        Observable.__init__(self)  # Initialize observer pattern
        self.labs: List[str] = []
        if config:
            self.load_labs(config)

    def load_labs(self, config: CombinedConfig) -> None:
        """
        Load labs from a CombinedConfig object and notify observers.

        Args:
            config: CombinedConfig object containing lab data
        """
        # Handle both CombinedConfig (config.config.labs) and SchedulerConfig (config.labs)
        if hasattr(config, "config") and hasattr(config.config, "labs"):
            labs_data = getattr(config.config, "labs", None)
            self.labs = list(labs_data) if labs_data else []
        elif hasattr(config, "labs"):
            labs_data = getattr(config, "labs", None)
            self.labs = list(labs_data) if labs_data else []
        else:
            self.labs = []
        
        # Notify observers that labs have been loaded
        self.notify_observers(
            EventType.LABS_LOADED,
            EventData(
                source=self,
                new_value=self.labs.copy(),
                count=len(self.labs)
            )
        )

    def add_lab(self, lab_name: str) -> bool:
        """
        Add a new lab and notify observers.

        Args:
            lab_name: Name of the lab to add

        Returns:
            True if lab was added, False if it already exists
        """
        if not lab_name:
            raise ValueError("Lab name cannot be empty")

        if lab_name in self.labs:
            return False

        self.labs.append(lab_name)
        
        # Notify observers of the new lab
        self.notify_observers(
            EventType.LAB_ADDED,
            EventData(
                source=self,
                new_value=lab_name,
                total_labs=len(self.labs)
            )
        )
        
        return True

    def delete_lab(self, lab_name: str) -> bool:
        """
        Delete a lab and notify observers.

        Args:
            lab_name: Name of the lab to delete

        Returns:
            True if lab was deleted, False if it doesn't exist
        """
        if lab_name not in self.labs:
            return False

        self.labs.remove(lab_name)
        
        # Notify observers of the deletion
        self.notify_observers(
            EventType.LAB_REMOVED,
            EventData(
                source=self,
                old_value=lab_name,
                total_labs=len(self.labs)
            )
        )
        
        return True

    def edit_lab(self, old_name: str, new_name: str) -> bool:
        """
        Rename a lab.

        Args:
            old_name: Current name of the lab
            new_name: New name for the lab

        Returns:
            True if lab was renamed, False if old_name doesn't exist or new_name already exists
        """
        if not new_name:
            raise ValueError("New lab name cannot be empty")

        if old_name not in self.labs:
            return False

        if new_name in self.labs:
            return False

        index = self.labs.index(old_name)
        self.labs[index] = new_name
        
        # Notify observers of the update
        self.notify_observers(
            EventType.LAB_UPDATED,
            EventData(
                source=self,
                old_value=old_name,
                new_value=new_name
            )
        )
        return True

    def get_labs(self) -> List[str]:
        """
        Get all labs.

        Returns:
            List of lab names
        """
        return self.labs.copy()

    def lab_exists(self, lab_name: str) -> bool:
        """
        Check if a lab exists.

        Args:
            lab_name: Name of the lab to check

        Returns:
            True if lab exists, False otherwise
        """
        return lab_name in self.labs

    def set_labs(self, labs: List[str]) -> None:
        """
        Replace all labs with a new list.

        Args:
            labs: New list of lab names
        """
        self.labs = list(labs)

    def to_dict(self) -> Dict:
        """
        Convert labs to a dictionary format compatible with SchedulerConfig.

        Returns:
            Dictionary with 'labs' key containing list of lab names
        """
        return {"labs": self.labs}

    def save_config(self, config: Dict) -> Dict:
        """
        Update a configuration dictionary with current lab data.

        Args:
            config: Dictionary configuration to update

        Returns:
            Updated configuration dictionary
        """
        config["labs"] = self.labs
        return config

    def save_with_combined_config(self, config: CombinedConfig) -> CombinedConfig:
        """
        Update a CombinedConfig object with current lab data.

        Args:
            config: CombinedConfig object to update

        Returns:
            Updated CombinedConfig object
        """
        # Update labs in the config
        config.config.labs = self.labs.copy()
        return config

    @staticmethod
    def update_lab_references(
        old_name: str, new_name: str, courses_dict: Dict, faculty_dict: Dict
    ) -> None:
        """
        Update lab references in courses and faculty when a lab is renamed.

        Args:
            old_name: Old lab name
            new_name: New lab name
            courses_dict: Dictionary of courses to update
            faculty_dict: Dictionary of faculty to update
        """
        # Update course lab assignments
        for course_id, instances in courses_dict.items():
            for course in instances:
                if hasattr(course, "lab") and old_name in course.lab:
                    course.lab = [new_name if lab_name == old_name else lab_name for lab_name in course.lab]

        # Update faculty lab preferences
        for name, faculty in faculty_dict.items():
            if (
                hasattr(faculty, "lab_preferences")
                and old_name in faculty.lab_preferences
            ):
                preference = faculty.lab_preferences[old_name]
                del faculty.lab_preferences[old_name]
                faculty.lab_preferences[new_name] = preference

    @staticmethod
    def remove_lab_references(
        lab_name: str, courses_dict: Dict, faculty_dict: Dict
    ) -> None:
        """
        Remove lab references from courses and faculty when a lab is deleted.

        Args:
            lab_name: Lab name to remove
            courses_dict: Dictionary of courses to update
            faculty_dict: Dictionary of faculty to update
        """
        # Remove from course lab assignments
        for course_id, instances in courses_dict.items():
            for course in instances:
                if hasattr(course, "lab") and lab_name in course.lab:
                    course.lab = [course_lab for course_lab in course.lab if course_lab != lab_name]

        # Remove from faculty lab preferences
        for name, faculty in faculty_dict.items():
            if (
                hasattr(faculty, "lab_preferences")
                and lab_name in faculty.lab_preferences
            ):
                del faculty.lab_preferences[lab_name]
