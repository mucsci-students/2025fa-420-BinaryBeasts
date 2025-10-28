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


