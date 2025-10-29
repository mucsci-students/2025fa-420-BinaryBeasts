# src/langchain_service.py
"""
Natural Language Processing Service using LangChain.
Handles LLM API interaction, prompt engineering, and intent extraction.
"""

import functools
import getpass
import os
from typing import Optional

from langchain.chat_models import init_chat_model
from langchain_core.tools import StructuredTool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field


# ============================================================================
# Pydantic Argument Schemas
# ============================================================================

class CourseAddSchema(BaseModel):
    """Schema for adding a course."""
    course_id: str = Field(description="The course ID (e.g., 'CMSC 201')")
    credits: int = Field(description="Number of credits for the course")


class CourseModifySchema(BaseModel):
    """Schema for modifying a course."""
    course_id: str = Field(description="The course ID to modify")
    field: str = Field(description="The field to modify (e.g., 'credits', 'room', 'lab', 'faculty')")
    value: str = Field(description="The new value for the field")


class CourseDeleteSchema(BaseModel):
    """Schema for deleting a course."""
    course_id: str = Field(description="The course ID to delete")


class FacultyAddSchema(BaseModel):
    """Schema for adding faculty."""
    name: str = Field(description="The faculty member's name")


class FacultyModifySchema(BaseModel):
    """Schema for modifying faculty."""
    name: str = Field(description="The faculty member's name")
    field: str = Field(description="The field to modify (e.g., 'minimum_credits', 'maximum_credits')")
    value: str = Field(description="The new value for the field")


class FacultyDeleteSchema(BaseModel):
    """Schema for deleting faculty."""
    name: str = Field(description="The faculty member's name to delete")


class RoomAddSchema(BaseModel):
    """Schema for adding a room."""
    name: str = Field(description="The room name (e.g., 'Roddy 147')")


class RoomModifySchema(BaseModel):
    """Schema for modifying a room."""
    old_name: str = Field(description="The current room name")
    new_name: str = Field(description="The new room name")


class RoomDeleteSchema(BaseModel):
    """Schema for deleting a room."""
    name: str = Field(description="The room name to delete")


class LabAddSchema(BaseModel):
    """Schema for adding a lab."""
    name: str = Field(description="The lab name (e.g., 'Linux Lab')")


class LabModifySchema(BaseModel):
    """Schema for modifying a lab."""
    old_name: str = Field(description="The current lab name")
    new_name: str = Field(description="The new lab name")


class LabDeleteSchema(BaseModel):
    """Schema for deleting a lab."""
    name: str = Field(description="The lab name to delete")


class ListSchema(BaseModel):
    """Schema for listing items (no arguments needed)."""
    pass


class ListCoursesSchema(BaseModel):
    """Schema for listing courses with optional faculty filter."""
    faculty_filter: Optional[str] = Field(default=None, description="Optional: Filter courses by faculty member name")


# ============================================================================
# Tool Wrapper Functions
# ============================================================================

def list_courses_wrapper(controller, faculty_filter: str = None) -> str:
    """Wrapper for listing all courses, optionally filtered by faculty."""
    courses_dict = controller.list_courses()
    if not courses_dict:
        return "No courses found"

    # Flatten the dict of lists into a single list
    all_courses = []
    for course_list in courses_dict.values():
        all_courses.extend(course_list)

    if not all_courses:
        return "No courses found"

    # Filter by faculty if provided
    if faculty_filter:
        faculty_filter = faculty_filter.strip()
        all_courses = [c for c in all_courses if faculty_filter in c.faculty]
        if not all_courses:
            return f"No courses found taught by {faculty_filter}"

    return "\n".join([f"• {c.course_id} ({c.credits} credits) - {', '.join(c.faculty)}" for c in all_courses])


def list_faculty_wrapper(controller) -> str:
    """Wrapper for listing all faculty."""
    faculty_dict = controller.list_faculty()
    if not faculty_dict:
        return "No faculty found"

    # Extract faculty objects from the dictionary
    faculty_list = list(faculty_dict.values())
    return "\n".join([f"• {f.name}" for f in faculty_list])


def list_rooms_wrapper(controller) -> str:
    """Wrapper for listing all rooms."""
    rooms = controller.get_rooms()
    if not rooms:
        return "No rooms found"
    return "\n".join([f"• {r}" for r in rooms])


def list_labs_wrapper(controller) -> str:
    """Wrapper for listing all labs."""
    labs = controller.get_labs()
    if not labs:
        return "No labs found"
    return "\n".join([f"• {l}" for l in labs])


# Add/Remove/Modify wrappers
def add_room_wrapper(controller, name: str) -> str:
    """Wrapper for adding a room."""
    if controller.room_exists(name):
        return f"Room {name} already exists"
    controller.add_room(name)
    return f"Room {name} added successfully"


def add_lab_wrapper(controller, name: str) -> str:
    """Wrapper for adding a lab."""
    if controller.lab_exists(name):
        return f"Lab {name} already exists"
    controller.add_lab(name)
    return f"Lab {name} added successfully"


def add_faculty_wrapper(controller, name: str) -> str:
    """Wrapper for adding a faculty member."""
    # Check if faculty exists
    faculty_dict = controller.list_faculty()
    if name in faculty_dict:
        return f"Faculty {name} already exists"

    # Create faculty data with defaults
    faculty_data = {
        "name": name,
        "minimum_credits": 0,
        "maximum_credits": 9,
        "unique_course_limit": 1,
        "times": {"MON": [], "TUE": [], "WED": [], "THU": [], "FRI": []},
        "course_preferences": {},
        "room_preferences": {},
        "lab_preferences": {},
    }
    controller.add_faculty(faculty_data)
    return f"Faculty {name} added successfully"


def remove_room_wrapper(controller, name: str) -> str:
    """Wrapper for removing a room."""
    if not controller.room_exists(name):
        return f"Room {name} does not exist"
    controller.delete_room(name)
    return f"Room {name} removed successfully"


def remove_lab_wrapper(controller, name: str) -> str:
    """Wrapper for removing a lab."""
    if not controller.lab_exists(name):
        return f"Lab {name} does not exist"
    controller.delete_lab(name)
    return f"Lab {name} removed successfully"


def rename_room_wrapper(controller, old_name: str, new_name: str) -> str:
    """Wrapper for renaming a room."""
    if not controller.room_exists(old_name):
        return f"Room {old_name} does not exist so it cannot be renamed"
    if controller.room_exists(new_name):
        return f"Room {new_name} already exists so it cannot be renamed from {old_name}"
    controller.edit_room(old_name, new_name)
    return f"Room {old_name} renamed to {new_name}"


def rename_lab_wrapper(controller, old_name: str, new_name: str) -> str:
    """Wrapper for renaming a lab."""
    if not controller.lab_exists(old_name):
        return f"Lab {old_name} does not exist so it cannot be renamed"
    if controller.lab_exists(new_name):
        return f"Lab {new_name} already exists so it cannot be renamed from {old_name}"
    controller.edit_lab(old_name, new_name)
    return f"Lab {old_name} renamed to {new_name}"


# ============================================================================
# LangChain Service Class
# ============================================================================

class LangChainService:
    """Service for processing natural language commands using LangChain."""

    def __init__(self):
        """Initialize LangChain service with API configuration."""
        self.model = None
        self.agent_executor = None

    def setup_agent(self, course_controller, faculty_controller,
                   lab_controller, room_controller) -> None:
        """
        Set up the agent with tools from controllers.

        Args:
            course_controller: Controller for course operations
            faculty_controller: Controller for faculty operations
            lab_controller: Controller for lab operations
            room_controller: Controller for room operations
        """
        # Get or prompt for API key
        if not os.environ.get("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

        # Initialize the chat model
        self.model = init_chat_model("gpt-5-mini", model_provider="openai")

        # Create tool list
        tools = self._create_tools(
            course_controller,
            faculty_controller,
            lab_controller,
            room_controller
        )

        # Create the agent executor
        self.agent_executor = create_react_agent(self.model, tools)

    def _create_tools(self, course_controller, faculty_controller,
                     lab_controller, room_controller) -> list[StructuredTool]:
        """
        Create LangChain tools from controller methods.

        Args:
            course_controller: Course controller
            faculty_controller: Faculty controller
            lab_controller: Lab controller
            room_controller: Room controller

        Returns:
            list[StructuredTool]: List of tools for the agent
        """
        return [
            # Course tools
            StructuredTool.from_function(
                name="list_courses",
                func=functools.partial(list_courses_wrapper, course_controller),
                description="List all courses in the system. Can optionally filter by faculty member name.",
                return_direct=True,
                args_schema=ListCoursesSchema,
            ),
            # Faculty tools
            StructuredTool.from_function(
                name="list_faculty",
                func=functools.partial(list_faculty_wrapper, faculty_controller),
                description="List all faculty members in the system",
                return_direct=True,
                args_schema=ListSchema,
            ),
            StructuredTool.from_function(
                name="add_faculty",
                func=functools.partial(add_faculty_wrapper, faculty_controller),
                description="Add a new faculty member to the system",
                return_direct=True,
                args_schema=FacultyAddSchema,
            ),
            # Room tools
            StructuredTool.from_function(
                name="list_rooms",
                func=functools.partial(list_rooms_wrapper, room_controller),
                description="List all rooms in the system",
                return_direct=True,
                args_schema=ListSchema,
            ),
            StructuredTool.from_function(
                name="add_room",
                func=functools.partial(add_room_wrapper, room_controller),
                description="Add a new room to the system",
                return_direct=True,
                args_schema=RoomAddSchema,
            ),
            StructuredTool.from_function(
                name="remove_room",
                func=functools.partial(remove_room_wrapper, room_controller),
                description="Remove a room from the system",
                return_direct=True,
                args_schema=RoomDeleteSchema,
            ),
            StructuredTool.from_function(
                name="rename_room",
                func=functools.partial(rename_room_wrapper, room_controller),
                description="Rename a room in the system",
                return_direct=True,
                args_schema=RoomModifySchema,
            ),
            # Lab tools
            StructuredTool.from_function(
                name="list_labs",
                func=functools.partial(list_labs_wrapper, lab_controller),
                description="List all labs in the system",
                return_direct=True,
                args_schema=ListSchema,
            ),
            StructuredTool.from_function(
                name="add_lab",
                func=functools.partial(add_lab_wrapper, lab_controller),
                description="Add a new lab to the system",
                return_direct=True,
                args_schema=LabAddSchema,
            ),
            StructuredTool.from_function(
                name="remove_lab",
                func=functools.partial(remove_lab_wrapper, lab_controller),
                description="Remove a lab from the system",
                return_direct=True,
                args_schema=LabDeleteSchema,
            ),
            StructuredTool.from_function(
                name="rename_lab",
                func=functools.partial(rename_lab_wrapper, lab_controller),
                description="Rename a lab in the system",
                return_direct=True,
                args_schema=LabModifySchema,
            ),
        ]

    def process_command(self, user_input: str) -> dict:
        """
        Process natural language command through the agent.

        Args:
            user_input: Natural language command from user

        Returns:
            dict: Result of command execution
                {
                    'success': bool,
                    'message': str,
                    'data': any
                }
        """
        if not self.agent_executor:
            return {
                'success': False,
                'message': 'Agent not initialized. Call setup_agent() first.',
                'data': None
            }

        try:
            # Invoke the agent with the user's message
            result = self.agent_executor.invoke({
                "messages": [HumanMessage(content=user_input)]
            })

            # Extract the response from messages (skip the first message which is the user's input)
            response_messages = []
            for message in result["messages"][1:]:
                if hasattr(message, 'content') and message.content:
                    response_messages.append(message.content)

            response_text = "\n".join(response_messages) if response_messages else "Command processed"

            return {
                'success': True,
                'message': response_text,
                'data': result
            }

        except Exception as e:
            return {
                'success': False,
                'message': f"Error processing command: {str(e)}",
                'data': None
            }