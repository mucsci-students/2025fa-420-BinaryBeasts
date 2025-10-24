# src/controllers/nl_controller.py
"""
Natural Language Controller.
Routes natural language commands to appropriate domain controllers.
"""

from src.langchain_service import LangChainService
from src.controllers.course_controller import CourseController
from src.controllers.faculty_controller import FacultyController
from src.controllers.lab_controller import LabController
from src.controllers.room_controller import RoomController


class NLController:
    """Controller for handling natural language commands."""

    def __init__(self, course_controller: CourseController,
                 faculty_controller: FacultyController,
                 lab_controller: LabController,
                 room_controller: RoomController):
        """
        Initialize NL controller with domain controllers.

        Args:
            course_controller: Controller for course operations
            faculty_controller: Controller for faculty operations
            lab_controller: Controller for lab operations
            room_controller: Controller for room operations
        """
        self.langchain_service = LangChainService()
        self.course_controller = course_controller
        self.faculty_controller = faculty_controller
        self.lab_controller = lab_controller
        self.room_controller = room_controller

        # Set up the agent with all controllers
        self.langchain_service.setup_agent(
            course_controller=course_controller,
            faculty_controller=faculty_controller,
            lab_controller=lab_controller,
            room_controller=room_controller
        )

    def process_command(self, user_input: str) -> dict:
        """
        Process natural language command and execute appropriate action.

        Args:
            user_input: Natural language command from user

        Returns:
            dict: Result of command execution
                {
                    'success': bool,
                    'message': str,
                    'data': any  # Result data if applicable
                }
        """
        # Use the langchain service to process the command
        return self.langchain_service.process_command(user_input)