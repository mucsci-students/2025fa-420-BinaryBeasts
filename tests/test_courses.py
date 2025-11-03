import json

from src.models.course_model import Course, CourseManager
from src.controllers.course_controller import CourseController


def test_course_creation():
    """Test basic Course object creation and validation."""
    # Valid course
    course = Course(
        course_id="CMSC 140",
        credits=4,
        room=["Roddy 136"],
        lab=[],
        conflicts=["CMSC 161"],
        faculty=[]
    )
    assert course.course_id == "CMSC 140"
    assert course.credits == 4
    assert course.room == ["Roddy 136"]


def test_course_manager_basic_operations():
    """Test basic CourseManager functionality."""
    mgr = CourseManager()

    # Sample course data
    course_data = [
        {
            "course_id": "CMSC 140",
            "credits": 4,
            "room": ["Roddy 136", "Roddy 140"],
            "lab": [],
            "conflicts": ["CMSC 161"],
            "faculty": []
        },
        {
            "course_id": "CMSC 161", 
            "credits": 4,
            "room": ["Roddy 136"],
            "lab": ["Linux"],
            "conflicts": ["CMSC 140"],
            "faculty": ["Zoppetti"]
        }
    ]

    # Load courses
    mgr.load_courses(course_data)
    
    # Check courses were loaded
    course_ids = mgr.get_course_ids()
    assert "CMSC 140" in course_ids
    assert "CMSC 161" in course_ids

    # Check resources were collected
    assert "Roddy 136" in mgr.rooms
    assert "Roddy 140" in mgr.rooms
    assert "Linux" in mgr.labs
    assert "Zoppetti" in mgr.faculty


def test_course_manager_add_course():
    """Test adding new courses to manager."""
    mgr = CourseManager()
    
    # Add a course
    new_course = Course(
        course_id="CMSC 170",
        credits=3,
        room=["Roddy 147"],
        lab=["Mac"],
        conflicts=[],
        faculty=["Doe"]
    )
    
    mgr.add_course(new_course)
    
    assert "CMSC 170" in mgr.get_course_ids()
    assert "Roddy 147" in mgr.rooms
    assert "Mac" in mgr.labs
    assert "Doe" in mgr.faculty


def test_course_controller_basic_flow(tmp_path):
    """Test CourseController basic operations."""
    mgr = CourseManager()
    controller = CourseController(mgr)

    # Sample course data
    course_data = {
        "course_id": "CMSC 152",
        "credits": 4,
        "room": ["Roddy 140"],
        "lab": ["Linux", "Mac"],
        "conflicts": [],
        "faculty": ["Hardy"]
    }

    # Add course via controller (add_course returns None)
    controller.add_course(course_data)
    # Verify it was added
    assert "CMSC 152" in controller.get_course_ids()
    
    # Check it exists
    assert "CMSC 152" in controller.get_course_ids()
    
    # Get course and verify data (get_course returns list)
    courses = controller.get_course("CMSC 152")
    assert len(courses) > 0
    course = courses[0] 
    assert course.course_id == "CMSC 152"
    assert course.credits == 4
    
    # Save to file
    out_file = tmp_path / "courses_out.json"
    success = controller.save_to_file({}, {}, str(out_file))
    assert success is True
    assert out_file.exists()
    
    # Verify file contents
    with open(out_file, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)
    assert 'config' in saved_data
    assert 'courses' in saved_data['config']


def test_course_controller_modify_delete():
    """Test modifying and deleting courses through controller."""
    mgr = CourseManager()
    controller = CourseController(mgr)

    # Add initial course
    course_data = {
        "course_id": "CMSC 240",
        "credits": 3,
        "room": ["Roddy 136"],
        "lab": [],
        "conflicts": [],
        "faculty": []
    }

    controller.add_course(course_data)
    assert "CMSC 240" in controller.get_course_ids()

    # Modify course (modify_course takes index parameter)
    modified_data = dict(course_data)
    modified_data["credits"] = 4
    modified_data["lab"] = ["Linux"]

    # Get first course (index 0) for this course_id
    assert controller.modify_course("CMSC 240", 0, modified_data) is True    # Verify modification (get_course returns list)
    updated_courses = controller.get_course("CMSC 240")
    assert len(updated_courses) > 0
    updated_course = updated_courses[0]
    assert updated_course.credits == 4
    assert "Linux" in updated_course.lab

    # Delete course (delete_course takes course_id and index)
    assert controller.delete_course("CMSC 240", 0) is True
    assert "CMSC 240" not in controller.get_course_ids()


def test_course_validation():
    """Test Course validation - invalid credits."""
    import pytest

    # Test empty course_id
    with pytest.raises(ValueError, match="Course ID cannot be empty"):
        Course(course_id="", credits=3)

    # Test zero credits
    with pytest.raises(ValueError, match="Credits must be positive"):
        Course(course_id="TEST 101", credits=0)

    # Test negative credits
    with pytest.raises(ValueError, match="Credits must be positive"):
        Course(course_id="TEST 101", credits=-1)


def test_course_manager_load_invalid_data():
    """Test CourseManager handles invalid course data gracefully."""
    mgr = CourseManager()

    # Valid and invalid course data
    course_data = [
        {
            "course_id": "VALID 101",
            "credits": 3,
            "room": ["Room A"],
            "lab": [],
            "conflicts": [],
            "faculty": []
        },
        {
            "course_id": "",  # Invalid - empty course_id
            "credits": 3,
        },
        {
            "course_id": "INVALID 102",
            "credits": 0,  # Invalid - zero credits
        }
    ]

    # Load courses - invalid ones should be skipped with warning
    mgr.load_courses(course_data)

    # Only valid course should be loaded
    assert "VALID 101" in mgr.get_course_ids()
    assert len(mgr.get_course_ids()) == 1


def test_delete_course_not_found():
    """Test deleting a course that doesn't exist."""
    mgr = CourseManager()

    # Try to delete non-existent course
    result = mgr.delete_course("NONEXISTENT 999", 0)

    # Should return False
    assert result is False


def test_modify_course_not_found():
    """Test modifying a course that doesn't exist."""
    mgr = CourseManager()

    # Create a new course
    new_course = Course(course_id="NEW 101", credits=3)

    # Try to modify non-existent course
    result = mgr.modify_course("NONEXISTENT 999", 0, new_course)

    # Should return False
    assert result is False


def test_modify_course_invalid_credits():
    """Test modifying a course with invalid credits."""
    import pytest
    mgr = CourseManager()

    # Add a course
    course = Course(course_id="TEST 101", credits=3)
    mgr.add_course(course)

    # Try to modify with invalid credits
    invalid_course = Course(course_id="TEST 101", credits=1)  # Create valid first
    invalid_course.credits = 0  # Then make invalid

    with pytest.raises(ValueError, match="Credits must be positive"):
        mgr.modify_course("TEST 101", 0, invalid_course)


def test_course_exists():
    """Test course_exists method."""
    mgr = CourseManager()

    # Add a course
    course = Course(course_id="CMSC 420", credits=4)
    mgr.add_course(course)

    # Test exists
    assert mgr.course_exists("CMSC 420") is True

    # Test doesn't exist
    assert mgr.course_exists("CMSC 999") is False


def test_get_conflicting_courses_no_manager():
    """Test get_conflicting_courses without conflict_manager."""
    mgr = CourseManager()

    # Add a course with conflicts
    course = Course(
        course_id="CMSC 140",
        credits=4,
        conflicts=["CMSC 161", "CMSC 162"]
    )
    mgr.add_course(course)

    # Get conflicts (should use course's conflict list since no manager)
    conflicts = mgr.get_conflicting_courses("CMSC 140")
    assert "CMSC 161" in conflicts
    assert "CMSC 162" in conflicts


def test_get_conflicting_courses_with_manager():
    """Test get_conflicting_courses with conflict_manager."""
    from unittest.mock import MagicMock

    mgr = CourseManager()

    # Create mock conflict manager
    mock_conflict_manager = MagicMock()
    mock_conflict_manager.get_conflicts.return_value = ["CMSC 999", "CMSC 888"]
    mgr.conflict_manager = mock_conflict_manager

    # Get conflicts (should use conflict_manager)
    conflicts = mgr.get_conflicting_courses("CMSC 140")

    # Verify conflict_manager was called
    mock_conflict_manager.get_conflicts.assert_called_once_with("CMSC 140")
    assert "CMSC 999" in conflicts
    assert "CMSC 888" in conflicts


def test_get_conflicting_courses_course_not_found():
    """Test get_conflicting_courses for non-existent course."""
    mgr = CourseManager()

    # Get conflicts for non-existent course
    conflicts = mgr.get_conflicting_courses("NONEXISTENT 999")

    # Should return empty set
    assert len(conflicts) == 0


def test_save_config_with_error(tmp_path):
    """Test save_config error handling."""
    mgr = CourseManager()

    # Add a course
    course = Course(course_id="TEST 101", credits=3)
    mgr.add_course(course)

    # Try to save to invalid path
    invalid_path = tmp_path / "nonexistent_dir" / "subdir" / "file.json"

    # Should return False due to error
    result = mgr.save_config({}, {}, str(invalid_path))
    assert result is False


def test_save_with_combined_config():
    """Test save_with_combined_config method (GUI-specific)."""
    from unittest.mock import MagicMock, patch

    mgr = CourseManager()

    # Add some courses
    course1 = Course(
        course_id="CMSC 140",
        credits=4,
        room=["Roddy 136"],
        lab=["Linux"],
        conflicts=["CMSC 161"],
        faculty=["Smith"]
    )
    course2 = Course(
        course_id="CMSC 161",
        credits=4,
        room=["Roddy 140"],
        lab=[],
        conflicts=["CMSC 140"],
        faculty=["Jones"]
    )
    mgr.add_course(course1)
    mgr.add_course(course2)

    # Create mock combined_config
    mock_combined_config = MagicMock()
    mock_editable_config = MagicMock()
    mock_config = MagicMock()
    mock_courses_list = MagicMock()

    # Set up the mock hierarchy
    mock_config.courses = mock_courses_list
    mock_editable_config.config = mock_config
    mock_combined_config.edit_mode.return_value.__enter__.return_value = mock_editable_config
    mock_combined_config.edit_mode.return_value.__exit__.return_value = None

    # Mock the CourseConfig import from scheduler.config
    with patch('scheduler.config.CourseConfig') as mock_course_config_class:
        mock_course_instances = []

        def create_course_config(*args, **kwargs):
            instance = MagicMock()
            mock_course_instances.append(instance)
            return instance

        mock_course_config_class.side_effect = create_course_config

        # Call the method
        result = mgr.save_with_combined_config(mock_combined_config)

        # Verify success
        assert result is True

        # Verify edit_mode was called
        mock_combined_config.edit_mode.assert_called_once()

        # Verify courses list was cleared
        mock_courses_list.clear.assert_called_once()

        # Verify CourseConfig was called for each course (2 times)
        assert mock_course_config_class.call_count == 2

        # Verify courses were appended to the list
        assert mock_courses_list.append.call_count == 2


def test_save_with_combined_config_error():
    """Test save_with_combined_config error handling."""
    from unittest.mock import MagicMock

    mgr = CourseManager()

    # Add a course
    course = Course(course_id="TEST 101", credits=3)
    mgr.add_course(course)

    # Create mock that raises an exception
    mock_combined_config = MagicMock()
    mock_combined_config.edit_mode.side_effect = Exception("Mock error")

    # Call should return False due to exception
    result = mgr.save_with_combined_config(mock_combined_config)

    # Should return False
    assert result is False


