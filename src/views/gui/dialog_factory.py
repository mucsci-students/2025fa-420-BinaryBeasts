"""
Dialog Factory for creating different types of manager dialogs.

This module implements the Factory design pattern to create dialog instances
for different management functionalities (courses, faculty, labs, rooms).
It provides a centralized way to create dialogs with their associated
controllers and managers.
"""

from src.views.gui.course_view_gui import CoursesDialog
from src.views.gui.faculty_gui import FacultiesDialog
from src.views.gui.lab_gui import LabsDialog
from src.views.gui.roomGui import RoomsDialog

from src.controllers.course_controller import CourseController
from src.controllers.faculty_controller import FacultyController
from src.controllers.lab_controller import LabController
from src.controllers.room_controller import RoomController

from src.models.course_model import CourseManager
from src.models.faculty_model import FacultyManager
from src.models.lab_model import LabManager
from src.models.room_model import RoomManager


class DialogFactory:
    """
    Factory class for creating dialog instances.
    
    This factory provides a centralized way to create different types of 
    manager dialogs along with their associated controllers and models.
    It encapsulates the complex initialization logic required for each
    dialog type.
    """
    
    @staticmethod
    def create_dialog(dialog_type, config, parent):
        """
        Create a dialog instance based on the specified type.
        
        Args:
            dialog_type (str): The type of dialog to create. 
                             Must be one of: 'courses', 'faculty', 'labs', 'rooms'
            config: The configuration object containing data for the dialog
            parent: The parent widget for the dialog
            
        Returns:
            QDialog: The created dialog instance
            
        Raises:
            ValueError: If dialog_type is not recognized
            Exception: If there's an error creating the dialog
        """
        if dialog_type == "courses":
            return DialogFactory._create_courses_dialog(config, parent)
            
        elif dialog_type == "faculty":
            return DialogFactory._create_faculty_dialog(config, parent)
            
        elif dialog_type == "labs":
            return DialogFactory._create_labs_dialog(config, parent)
            
        elif dialog_type == "rooms":
            return DialogFactory._create_rooms_dialog(config, parent)
            
        else:
            raise ValueError(f"Unknown dialog type: {dialog_type}")
    
    @staticmethod
    def _create_courses_dialog(config, parent):
        """Create and configure a courses management dialog."""
        # Create course manager
        course_manager = CourseManager()
        
        # Extract and format courses data from config
        courses_data = []
        for course in config.config.courses:
            courses_data.append({
                "course_id": course.course_id,
                "credits": course.credits,
                "room": list(course.room) if hasattr(course.room, "__iter__") else [course.room],
                "lab": list(course.lab) if hasattr(course.lab, "__iter__") else [course.lab],
                "faculty": list(course.faculty) if hasattr(course.faculty, "__iter__") else [course.faculty],
                "conflicts": list(course.conflicts) if hasattr(course.conflicts, "__iter__") else [course.conflicts],
            })
        
        # Load data into manager
        course_manager.load_courses(courses_data)
        
        # Create controller
        controller = CourseController(course_manager)
        
        # Create and return dialog
        return CoursesDialog(controller, config, parent)
    
    @staticmethod
    def _create_faculty_dialog(config, parent):
        """Create and configure a faculty management dialog."""
        # Create faculty manager
        faculty_manager = FacultyManager()
        
        # Extract and format faculty data from config
        faculty_data = []
        for faculty in config.config.faculty:
            faculty_data.append({
                "name": faculty.name,
                "minimum_credits": faculty.minimum_credits,
                "maximum_credits": faculty.maximum_credits,
                "unique_course_limit": faculty.unique_course_limit,
                "times": dict(faculty.times) if hasattr(faculty, "times") else {},
                "course_preferences": dict(faculty.course_preferences) if hasattr(faculty, "course_preferences") else {},
                "room_preferences": dict(faculty.room_preferences) if hasattr(faculty, "room_preferences") else {},
                "lab_preferences": dict(faculty.lab_preferences) if hasattr(faculty, "lab_preferences") else {},
            })
        
        # Load data into manager
        faculty_manager.load_faculty(faculty_data)
        
        # Create controller
        controller = FacultyController(faculty_manager)
        
        # Create and return dialog
        return FacultiesDialog(controller, config, parent)
    
    @staticmethod
    def _create_labs_dialog(config, parent):
        """Create and configure a labs management dialog."""
        # Create lab manager with config
        lab_manager = LabManager(config)
        
        # Create controller
        controller = LabController(lab_manager)
        
        # Create and return dialog
        return LabsDialog(controller, config, parent)
    
    @staticmethod
    def _create_rooms_dialog(config, parent):
        """Create and configure a rooms management dialog."""
        # Create room manager with config
        room_manager = RoomManager(config)
        
        # Create controller
        controller = RoomController(room_manager)
        
        # Create and return dialog
        return RoomsDialog(controller, config, parent)


class DialogType:
    """Constants for dialog types to avoid string literals in client code."""
    COURSES = "courses"
    FACULTY = "faculty"
    LABS = "labs"
    ROOMS = "rooms"
