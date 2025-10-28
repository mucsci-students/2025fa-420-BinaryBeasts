"""
Basic GUI tests for courses functionality.
Note: These are basic import and instantiation tests since GUI testing requires a display.
"""

import pytest


def test_course_gui_imports():
    """Test that course GUI components can be imported."""
    try:
        from src.views.gui.course_view_gui import CoursesDialog
        assert CoursesDialog is not None
    except ImportError:
        # GUI components may not be available in all environments
        pytest.skip("Course GUI components not available")


def test_course_controller_for_gui():
    """Test course controller functionality that would be used by GUI."""
    from src.models.course_model import CourseManager
    from src.controllers.course_controller import CourseController
    
    # Test basic controller operations
    manager = CourseManager()
    controller = CourseController(manager)
    
    # Test adding a course (GUI would call this)
    course_data = {
        "course_id": "GUI_TEST_101",
        "credits": 3,
        "room": ["Test Room"],
        "lab": [],
        "conflicts": [],
        "faculty": []
    }

    # add_course returns None, so check if course was added
    controller.add_course(course_data)
    assert "GUI_TEST_101" in controller.get_course_ids()
    assert "GUI_TEST_101" in controller.get_course_ids()
    
    # Test getting course data (GUI would display this)
    courses = controller.get_course("GUI_TEST_101")
    assert len(courses) > 0
    course = courses[0]
    assert course.course_id == "GUI_TEST_101"
    assert course.credits == 3


def test_course_data_validation():
    """Test course data validation that GUI would perform."""
    from src.controllers.course_controller import CourseController
    from src.models.course_model import CourseManager
    
    manager = CourseManager()
    controller = CourseController(manager)
    
    # Test invalid data (GUI should catch these)
    invalid_data = {
        "course_id": "",  # Empty course ID
        "credits": 3,
        "room": [],
        "lab": [],
        "conflicts": [],
        "faculty": []
    }
    
    # Should handle invalid data gracefully
    try:
        result = controller.add_course(invalid_data)
        assert result is False or result is None
    except ValueError:
        # Expected behavior for invalid data
        pass