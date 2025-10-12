# tests/test_course_model.py
import pytest
from course_model import Course, CourseManager


class TestCourse:
    """Test Course class."""

    def test_course_creation(self):
        """Test creating a valid course."""
        course = Course(
            course_id="CMSC 101",
            credits=3,
            room=["R101"],
            lab=["L101"],
            faculty=["Dr. Smith"],
            conflicts=["CMSC 102"]
        )
        assert course.course_id == "CMSC 101"
        assert course.credits == 3
        assert course.room == ["R101"]

    def test_course_empty_id_raises_error(self):
        """Test that empty course ID raises error."""
        with pytest.raises(ValueError, match="Course ID cannot be empty"):
            Course(course_id="", credits=3)

    def test_course_negative_credits_raises_error(self):
        """Test that negative credits raises error."""
        with pytest.raises(ValueError, match="Credits must be positive"):
            Course(course_id="CMSC 101", credits=0)

    def test_course_default_values(self):
        """Test course with default empty lists."""
        course = Course(course_id="CMSC 101", credits=3)
        assert course.room == []
        assert course.lab == []
        assert course.faculty == []
        assert course.conflicts == []


class TestCourseManager:
    """Test CourseManager class."""

    def test_add_course(self):
        """Test adding a course."""
        manager = CourseManager()
        course = Course(course_id="CMSC 101", credits=3)
        manager.add_course(course)

        assert "CMSC 101" in manager.courses
        assert len(manager.get_course("CMSC 101")) == 1

    def test_add_multiple_instances(self):
        """Test adding multiple instances of same course."""
        manager = CourseManager()
        course1 = Course(course_id="CMSC 101", credits=3, room=["R101"])
        course2 = Course(course_id="CMSC 101", credits=3, room=["R102"])

        manager.add_course(course1)
        manager.add_course(course2)

        instances = manager.get_course("CMSC 101")
        assert len(instances) == 2

    def test_delete_course(self):
        """Test deleting a course."""
        manager = CourseManager()
        course = Course(course_id="CMSC 101", credits=3)
        manager.add_course(course)

        result = manager.delete_course("CMSC 101", 0)
        assert result == True
        assert "CMSC 101" not in manager.courses

    def test_delete_nonexistent_course(self):
        """Test deleting a course that doesn't exist."""
        manager = CourseManager()
        result = manager.delete_course("CMSC 999", 0)
        assert result == False

    def test_modify_course(self):
        """Test modifying a course."""
        manager = CourseManager()
        course = Course(course_id="CMSC 101", credits=3, room=["R101"])
        manager.add_course(course)

        new_course = Course(course_id="CMSC 101", credits=4, room=["R102"])
        result = manager.modify_course("CMSC 101", 0, new_course)

        assert result == True
        modified = manager.get_course("CMSC 101")[0]
        assert modified.credits == 4
        assert modified.room == ["R102"]

    def test_get_resources(self):
        """Test resource collection."""
        manager = CourseManager()
        course1 = Course(course_id="CMSC 101", credits=3,
                         room=["R101"], lab=["L101"], faculty=["Dr. Smith"])
        course2 = Course(course_id="CMSC 102", credits=3,
                         room=["R102"], lab=["L102"], faculty=["Dr. Jones"])

        manager.add_course(course1)
        manager.add_course(course2)

        assert "R101" in manager.rooms
        assert "R102" in manager.rooms
        assert "L101" in manager.labs
        assert "Dr. Smith" in manager.faculty

    def test_load_courses_from_data(self):
        """Test loading courses from dictionary data."""
        manager = CourseManager()
        data = [
            {
                'course_id': 'CMSC 101',
                'credits': 3,
                'room': ['R101'],
                'lab': ['L101'],
                'faculty': ['Dr. Smith'],
                'conflicts': []
            },
            {
                'course_id': 'CMSC 102',
                'credits': 4,
                'room': ['R102'],
                'lab': [],
                'faculty': ['Dr. Jones'],
                'conflicts': ['CMSC 101']
            }
        ]

        manager.load_courses(data)
        assert len(manager.get_all_courses()) == 2
        assert manager.course_exists("CMSC 101")
        assert manager.course_exists("CMSC 102")

    def test_to_dict(self):
        """Test converting courses to dictionary format."""
        manager = CourseManager()
        course = Course(course_id="CMSC 101", credits=3, room=["R101"])
        manager.add_course(course)

        result = manager.to_dict()
        assert len(result) == 1
        assert result[0]['course_id'] == "CMSC 101"
        assert result[0]['credits'] == 3
        assert result[0]['room'] == ["R101"]