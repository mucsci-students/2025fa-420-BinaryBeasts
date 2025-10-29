# tests/test_langchain_service.py
"""
Basic tests for AI Assistant functionality.
Tests the main user-facing features without getting too complex.
"""

import pytest
from unittest.mock import Mock, patch
from src.langchain_service import (
    LangChainService,
    list_courses_wrapper,
    list_faculty_wrapper,
    list_rooms_wrapper,
    list_labs_wrapper,
)
from src.models.course_model import CourseManager
from src.models.faculty_model import FacultyManager
from src.controllers.course_controller import CourseController
from src.controllers.faculty_controller import FacultyController


# ============================================================================
# Basic Tool Wrapper Tests
# ============================================================================

def test_list_courses_shows_course_info():
    """Test that listing courses shows course IDs and credits."""
    manager = CourseManager()
    manager.load_courses([
        {
            "course_id": "CMSC 140",
            "credits": 4,
            "room": ["Roddy 136"],
            "lab": [],
            "conflicts": [],
            "faculty": []
        }
    ])
    controller = CourseController(manager)
    result = list_courses_wrapper(controller)

    assert "CMSC 140" in result
    assert "4 credits" in result


def test_list_courses_when_empty():
    """Test listing courses when no courses exist."""
    manager = CourseManager()
    controller = CourseController(manager)
    result = list_courses_wrapper(controller)

    assert result == "No courses found"


def test_list_faculty_shows_names():
    """Test that listing faculty shows faculty names."""
    manager = FacultyManager()
    manager.load_faculty([
        {
            "name": "Dr. Smith",
            "minimum_credits": 8,
            "maximum_credits": 12,
            "unique_course_limit": 3,
            "times": {"MON": [], "TUE": [], "WED": [], "THU": [], "FRI": []},
            "course_preferences": {},
            "room_preferences": {},
            "lab_preferences": {},
        }
    ])
    controller = FacultyController(manager)
    result = list_faculty_wrapper(controller)

    assert "Dr. Smith" in result


# ============================================================================
# Basic Service Tests
# ============================================================================

def test_service_starts_uninitialized():
    """Test that service starts without agent set up."""
    service = LangChainService()

    assert service.model is None
    assert service.agent_executor is None


def test_process_command_fails_without_setup():
    """Test that processing commands fails if agent not set up."""
    service = LangChainService()
    result = service.process_command("list courses")

    assert result['success'] is False
    assert "not initialized" in result['message'].lower()


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-api-key'})
@patch('src.langchain_service.init_chat_model')
@patch('src.langchain_service.create_react_agent')
def test_agent_setup_works(mock_create_agent, mock_init_model):
    """Test that agent can be set up with mocked API."""
    # Mock the LLM and agent
    mock_model = Mock()
    mock_init_model.return_value = mock_model
    mock_agent = Mock()
    mock_create_agent.return_value = mock_agent

    # Create controllers
    course_mgr = CourseManager()
    course_controller = CourseController(course_mgr)
    faculty_mgr = FacultyManager()
    faculty_controller = FacultyController(faculty_mgr)

    # Mock lab and room controllers
    lab_controller = Mock()
    lab_controller.get_labs.return_value = ["Linux", "Mac"]
    room_controller = Mock()
    room_controller.get_rooms.return_value = ["Roddy 136", "Roddy 140"]

    # Setup service
    service = LangChainService()
    service.setup_agent(
        course_controller,
        faculty_controller,
        lab_controller,
        room_controller
    )

    # Verify it was set up
    assert service.model == mock_model
    assert service.agent_executor == mock_agent


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-api-key'})
@patch('src.langchain_service.init_chat_model')
@patch('src.langchain_service.create_react_agent')
def test_process_command_returns_response(mock_create_agent, mock_init_model):
    """Test that processing a command returns a response."""
    # Mock the LLM and agent
    mock_model = Mock()
    mock_init_model.return_value = mock_model

    # Mock agent to return a response
    mock_message = Mock()
    mock_message.content = "Here are the courses: CMSC 140"
    mock_agent = Mock()
    mock_agent.invoke.return_value = {
        "messages": [Mock(), mock_message]  # First is user message, second is response
    }
    mock_create_agent.return_value = mock_agent

    # Setup service
    service = LangChainService()
    service.setup_agent(Mock(), Mock(), Mock(), Mock())

    # Process command
    result = service.process_command("list courses")

    # Verify response
    assert result['success'] is True
    assert "CMSC 140" in result['message']


@patch.dict('os.environ', {'OPENAI_API_KEY': 'test-api-key'})
@patch('src.langchain_service.init_chat_model')
@patch('src.langchain_service.create_react_agent')
def test_process_command_handles_errors(mock_create_agent, mock_init_model):
    """Test that errors are handled gracefully."""
    mock_init_model.return_value = Mock()

    # Mock agent to raise an error
    mock_agent = Mock()
    mock_agent.invoke.side_effect = Exception("API Error")
    mock_create_agent.return_value = mock_agent

    service = LangChainService()
    service.setup_agent(Mock(), Mock(), Mock(), Mock())

    result = service.process_command("list courses")

    # Should return error result
    assert result['success'] is False
    assert "Error" in result['message']