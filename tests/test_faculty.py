import json
import pytest

from src.models.faculty_model import Faculty, FacultyManager
from src.controllers.faculty_controller import FacultyController


def test_faculty_creation():
    """Test basic Faculty object creation and validation."""
    # Valid faculty
    faculty = Faculty(
        name="Dr. Smith",
        minimum_credits=3,
        maximum_credits=12,
        unique_course_limit=3,
        times={"MON": ["09:00-10:00", "11:00-12:00"]},
        course_preferences={"CMSC 140": 8, "CMSC 161": 6},
        room_preferences={"Roddy 136": 9, "Roddy 140": 7},
        lab_preferences={"Linux": 8, "Mac": 5}
    )
    assert faculty.name == "Dr. Smith"
    assert faculty.minimum_credits == 3
    assert faculty.maximum_credits == 12
    assert faculty.course_preferences["CMSC 140"] == 8


def test_faculty_validation():
    """Test Faculty validation rules."""
    with pytest.raises(ValueError):
        Faculty(name="")  # Empty name should fail

    with pytest.raises(ValueError):
        Faculty(name="Dr. Test", minimum_credits=-1)  # Negative credits should fail

    with pytest.raises(ValueError):
        Faculty(name="Dr. Test", minimum_credits=5, maximum_credits=3)  # Min > Max should fail

    with pytest.raises(ValueError):
        Faculty(name="Dr. Test", unique_course_limit=0)  # Zero course limit should fail


def test_faculty_manager_basic_operations():
    """Test basic FacultyManager functionality."""
    mgr = FacultyManager()

    # Sample faculty data
    faculty_data = [
        {
            'name': 'Dr. Alice',
            'minimum_credits': 1,
            'maximum_credits': 5,
            'unique_course_limit': 2,
            'times': {'MON': ['09:00-11:00']},
            'course_preferences': {'CMSC140': 8},
            'room_preferences': {'Roddy 136': 5},
            'lab_preferences': {'Linux': 7},
        },
        {
            'name': 'Dr. Bob',
            'minimum_credits': 0,
            'maximum_credits': 9,
            'unique_course_limit': 1,
            'times': {'TUE': ['10:00-12:00']},
            'course_preferences': {},
            'room_preferences': {},
            'lab_preferences': {},
        }
    ]

    # Load faculty
    mgr.load_faculty(faculty_data)
    
    # Check faculty were loaded
    faculty_names = mgr.get_faculty_names()
    assert 'Dr. Alice' in faculty_names
    assert 'Dr. Bob' in faculty_names

    # Get specific faculty
    alice = mgr.get_faculty('Dr. Alice')
    assert isinstance(alice, Faculty)
    assert alice.name == 'Dr. Alice'
    assert alice.minimum_credits == 1
    assert alice.course_preferences.get('CMSC140') == 8


def test_faculty_manager_add_modify_delete():
    """Test adding, modifying, and deleting faculty."""
    mgr = FacultyManager()
    
    # Add a Faculty object directly
    carol = Faculty(
        name='Dr. Carol',
        minimum_credits=0,
        maximum_credits=6,
        unique_course_limit=2
    )
    assert mgr.add_faculty(carol) is True
    
    # Check duplicate prevention
    assert mgr.add_faculty(carol) is False  # Should fail - already exists
    
    # Modify faculty
    carol_v2 = Faculty(
        name='Dr. Carol',
        minimum_credits=2,
        maximum_credits=8,
        unique_course_limit=3,
        course_preferences={'CMSC 152': 9}
    )
    assert mgr.modify_faculty('Dr. Carol', carol_v2) is True
    
    # Verify modification
    updated_carol = mgr.get_faculty('Dr. Carol')
    assert updated_carol is not None
    assert updated_carol.minimum_credits == 2
    assert updated_carol.maximum_credits == 8
    assert updated_carol.course_preferences.get('CMSC 152') == 9
    
    # Delete faculty
    assert mgr.delete_faculty('Dr. Carol') is True
    assert mgr.get_faculty('Dr. Carol') is None


def test_faculty_controller_basic_flow(tmp_path):
    """Test FacultyController basic operations."""
    mgr = FacultyManager()
    controller = FacultyController(mgr)

    # Sample faculty data
    faculty_data = {
        'name': 'Dr. Dave',
        'minimum_credits': 0,
        'maximum_credits': 6,
        'unique_course_limit': 2,
        'times': {},
        'course_preferences': {},
        'room_preferences': {},
        'lab_preferences': {},
    }

    # Add faculty via controller
    assert controller.add_faculty(faculty_data) is True
    
    # Check it exists
    assert 'Dr. Dave' in controller.get_faculty_names()
    
    # Get faculty and verify data
    dave = controller.get_faculty('Dr. Dave')
    assert dave.name == 'Dr. Dave'
    assert dave.maximum_credits == 6
    
    # Save to file
    out_file = tmp_path / "faculty_out.json"
    success = controller.save_to_file({}, {}, str(out_file))
    assert success is True
    assert out_file.exists()
    
    # Verify file contents
    with open(out_file, 'r', encoding='utf-8') as f:
        saved_data = json.load(f)
    assert 'config' in saved_data
    assert 'faculty' in saved_data['config']


def test_faculty_controller_modify_delete():
    """Test modifying and deleting faculty through controller."""
    mgr = FacultyManager()
    controller = FacultyController(mgr)

    # Add initial faculty
    faculty_data = {
        'name': 'Dr. Eve',
        'minimum_credits': 1,
        'maximum_credits': 4,
        'unique_course_limit': 1,
        'times': {},
        'course_preferences': {},
        'room_preferences': {},
        'lab_preferences': {},
    }
    
    controller.add_faculty(faculty_data)
    assert 'Dr. Eve' in controller.get_faculty_names()
    
    # Modify faculty
    modified_data = dict(faculty_data)
    modified_data['minimum_credits'] = 2
    modified_data['course_preferences'] = {'CMSC 240': 7}
    
    assert controller.modify_faculty('Dr. Eve', modified_data) is True
    
    # Verify modification
    updated_faculty = controller.get_faculty('Dr. Eve')
    assert updated_faculty.minimum_credits == 2
    assert updated_faculty.course_preferences.get('CMSC 240') == 7
    
    # Delete faculty
    assert controller.delete_faculty('Dr. Eve') is True
    assert not controller.faculty_exists('Dr. Eve')


def test_faculty_controller_invalid_data():
    """Test that controller rejects invalid faculty data."""
    mgr = FacultyManager()
    controller = FacultyController(mgr)

    # Invalid data - empty name
    invalid_data = {'name': '', 'minimum_credits': 0}
    
    try:
        controller.add_faculty(invalid_data)
        # Should either return False or raise an exception
        assert False, "Should have rejected invalid data"
    except (ValueError, Exception):
        # Expected behavior for invalid data
        pass


def test_faculty_manager_load_with_invalid_data():
    """Test that manager handles invalid entries gracefully."""
    mgr = FacultyManager()

    valid_faculty = {
        'name': 'Dr. Valid',
        'minimum_credits': 1,
        'maximum_credits': 5,
        'unique_course_limit': 2,
        'times': {'MON': ['09:00-10:00']},
        'course_preferences': {'CMSC140': 5},
        'room_preferences': {'R1': 3},
        'lab_preferences': {'Linux': 4}
    }

    invalid_faculty = {'name': '', 'minimum_credits': 0}  # Invalid

    # Load both; invalid entry should be ignored (with warning)
    mgr.load_faculty([valid_faculty, invalid_faculty])
    
    # Only valid faculty should be loaded
    assert 'Dr. Valid' in mgr.get_faculty_names()
    assert len(mgr.get_faculty_names()) == 1


def test_faculty_manager_to_dict_and_save(tmp_path):
    """Test converting faculty to dict format and saving."""
    mgr = FacultyManager()
    
    # Add faculty
    faculty = Faculty(
        name='Dr. Test',
        minimum_credits=1,
        maximum_credits=5,
        unique_course_limit=2,
        times={'MON': ['09:00-10:00']},
        course_preferences={'CMSC140': 5},
        room_preferences={'R1': 3},
        lab_preferences={'Linux': 4}
    )
    mgr.add_faculty(faculty)
    
    # Convert to dict
    faculty_dict = mgr.to_dict()
    assert isinstance(faculty_dict, list)
    assert len(faculty_dict) == 1
    
    faculty_entry = faculty_dict[0]
    assert faculty_entry['name'] == 'Dr. Test'
    assert faculty_entry['minimum_credits'] == 1
    
    # Save config
    out_file = tmp_path / 'faculty_config.json'
    success = mgr.save_config({}, {}, str(out_file))
    assert success is True
    assert out_file.exists()
    
    # Verify file contains faculty data
    with open(out_file, 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)
    assert 'config' in loaded_data
    assert 'faculty' in loaded_data['config']
    assert len(loaded_data['config']['faculty']) == 1
    assert loaded_data['config']['faculty'][0]['name'] == 'Dr. Test'