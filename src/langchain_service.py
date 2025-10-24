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


# ============================================================================
# Tool Wrapper Functions
# ============================================================================

def list_courses_wrapper(controller) -> str:
    """Wrapper for listing all courses."""
    courses_dict = controller.list_courses()
    if not courses_dict:
        return "No courses found"

    # Flatten the dict of lists into a single list
    all_courses = []
    for course_list in courses_dict.values():
        all_courses.extend(course_list)

    if not all_courses:
        return "No courses found"

    return "\n".join([f"• {c.course_id} ({c.credits} credits)" for c in all_courses])


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
                description="List all courses in the system",
                return_direct=True,
                args_schema=ListSchema,
            ),
            # Faculty tools
            StructuredTool.from_function(
                name="list_faculty",
                func=functools.partial(list_faculty_wrapper, faculty_controller),
                description="List all faculty members in the system",
                return_direct=True,
                args_schema=ListSchema,
            ),
            # Room tools
            StructuredTool.from_function(
                name="list_rooms",
                func=functools.partial(list_rooms_wrapper, room_controller),
                description="List all rooms in the system",
                return_direct=True,
                args_schema=ListSchema,
            ),
            # Lab tools
            StructuredTool.from_function(
                name="list_labs",
                func=functools.partial(list_labs_wrapper, lab_controller),
                description="List all labs in the system",
                return_direct=True,
                args_schema=ListSchema,
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