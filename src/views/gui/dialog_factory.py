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
from src.views.gui.timeslot_gui import TimeSlotsDialog

from src.controllers.course_controller import CourseController
from src.controllers.faculty_controller import FacultyController
from src.controllers.lab_controller import LabController
from src.controllers.room_controller import RoomController
from src.controllers.time_slot_controller import TimeSlotController

from src.models.course_model import CourseManager
from src.models.faculty_model import FacultyManager
from src.models.lab_model import LabManager
from src.models.room_model import RoomManager
from src.models.time_slot_model import TimeSlotManager
from src.undo_manager import SnapshotUndoManager


class DialogFactory:
    """
    Factory class for creating dialog instances.
    
    This factory provides a centralized way to create different types of 
    manager dialogs along with their associated controllers and models.
    It encapsulates the complex initialization logic required for each
    dialog type.
    """
    
    @staticmethod
    def create_dialog(dialog_type, config, parent, conflict_observer=None):
        """
        Create a dialog instance based on the specified type.
        
        Args:
            dialog_type (str): The type of dialog to create. 
                             Must be one of: 'courses', 'faculty', 'labs', 'rooms'
            config: The configuration object containing data for the dialog
            parent: The parent widget for the dialog
            conflict_observer: Optional conflict resolution observer for cross-manager dependencies
            
        Returns:
            QDialog: The created dialog instance
            
        Raises:
            ValueError: If dialog_type is not recognized
            Exception: If there's an error creating the dialog
        """
        if dialog_type == "courses":
            return DialogFactory._create_courses_dialog(config, parent, conflict_observer)
            
        elif dialog_type == "faculty":
            return DialogFactory._create_faculty_dialog(config, parent, conflict_observer)
            
        elif dialog_type == "labs":
            return DialogFactory._create_labs_dialog(config, parent, conflict_observer)
            
        elif dialog_type == "rooms":
            return DialogFactory._create_rooms_dialog(config, parent, conflict_observer)
            
        elif dialog_type == "timeslots":
            return DialogFactory._create_timeslots_dialog(config, parent, conflict_observer)
            
        else:
            raise ValueError(f"Unknown dialog type: {dialog_type}")
    
    @staticmethod
    def _create_courses_dialog(config, parent, conflict_observer=None):
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

        # Load data into manager (this will trigger COURSES_LOADED event)
        course_manager.load_courses(courses_data)

        undo_manager = SnapshotUndoManager(
            get_state=course_manager.snapshot_state,
            set_state=course_manager.restore_state,
        )

        # Attach conflict resolution observer if provided
        if conflict_observer and hasattr(course_manager, 'add_observer'):
            course_manager.add_observer(conflict_observer)
            conflict_observer.register_manager('course', course_manager)

        # Create controller
        controller = CourseController(course_manager, undo_manager=undo_manager)
        # Create and return dialog
        return CoursesDialog(controller, config, parent)

    @staticmethod
    def _create_faculty_dialog(config, parent, conflict_observer=None):
        """Create and configure a faculty management dialog."""
        # Create faculty manager
        faculty_manager = FacultyManager()
        
        # Attach conflict resolution observer if provided
        if conflict_observer and hasattr(faculty_manager, 'add_observer'):
            faculty_manager.add_observer(conflict_observer)
            conflict_observer.register_manager('faculty', faculty_manager)
        
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
        
        # Load data into manager (this will trigger FACULTY_LOADED event)
        faculty_manager.load_faculty(faculty_data)

        faculty_undo = SnapshotUndoManager(
            get_state=faculty_manager.snapshot_state,
            set_state=faculty_manager.restore_state,
        )

        # Create controller
        controller = FacultyController(faculty_manager, undo_manager=faculty_undo)
        
        # Create and return dialog
        return FacultiesDialog(controller, config, parent)
    
    @staticmethod
    def _create_labs_dialog(config, parent, conflict_observer=None):
        """Create and configure a labs management dialog."""
        # Create lab manager with config
        lab_manager = LabManager(config)

        lab_undo = SnapshotUndoManager(
            get_state=lab_manager.snapshot_state,
            set_state=lab_manager.restore_state,
        )

        # Attach conflict resolution observer if provided
        if conflict_observer and hasattr(lab_manager, 'add_observer'):
            lab_manager.add_observer(conflict_observer)
            conflict_observer.register_manager('lab', lab_manager)
        
        # Create controller
        controller = LabController(lab_manager, undo_manager=lab_undo)
        
        # Create and return dialog
        return LabsDialog(controller, config, parent)
    
    @staticmethod
    def _create_rooms_dialog(config, parent, conflict_observer=None):
        """Create and configure a rooms management dialog."""
        # Create room manager with config
        room_manager = RoomManager(config)
        room_undo = SnapshotUndoManager(
            get_state=room_manager.snapshot_state,
            set_state=room_manager.restore_state,
        )

        # Attach conflict resolution observer if provided
        if conflict_observer and hasattr(room_manager, 'add_observer'):
            room_manager.add_observer(conflict_observer)
            conflict_observer.register_manager('room', room_manager)
        
        # Create controller
        controller = RoomController(room_manager, undo_manager=room_undo)
        
        # Create and return dialog
        return RoomsDialog(controller, config, parent)

    @staticmethod
    def _create_timeslots_dialog(config, parent, conflict_observer=None):
        """Create and configure a time slots management dialog."""
        # Create time slot manager
        timeslot_manager = TimeSlotManager()

        # Load time slot configuration from the combined config
        if hasattr(config, 'time_slot_config') and config.time_slot_config:
            time_slot_config = config.time_slot_config

            # Convert TimeSlotConfig object to dictionary format
            try:
                # Try Pydantic v2 method first
                config_dict = time_slot_config.model_dump()
            except AttributeError:
                try:
                    # Try Pydantic v1 method
                    config_dict = time_slot_config.dict()
                except AttributeError:
                    # If it's already a dictionary
                    config_dict = time_slot_config

            # Load the dictionary configuration
            timeslot_manager.load_time_slots(config_dict)
        
        timeslot_manager = TimeSlotManager(config)

        # Attach conflict resolution observer if provided
        if conflict_observer and hasattr(timeslot_manager, 'add_observer'):
            timeslot_manager.add_observer(conflict_observer)
            conflict_observer.register_manager('timeslot', timeslot_manager)

        # Create undo/redo manager for time slots
        undo_manager = SnapshotUndoManager(
            get_state=timeslot_manager.snapshot_state,
            set_state=timeslot_manager.restore_state,
        )

        # Create controller with undo manager
        controller = TimeSlotController(timeslot_manager, undo_manager=undo_manager)

        # Create and return dialog
        return TimeSlotsDialog(controller, config, parent)


class DialogType:
    """Constants for dialog types to avoid string literals in client code."""
    COURSES = "courses"
    FACULTY = "faculty"
    LABS = "labs"
    ROOMS = "rooms"
    TIMESLOTS = "timeslots"
