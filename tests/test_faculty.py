import json
import pytest

from src.models.faculty_model import Faculty, FacultyManager
from src.controllers.faculty_controller import FacultyController


def test_faculty_manager_basic_operations():
    mgr = FacultyManager()

    # load a faculty entry via dict
    entry = {
        'name': 'Dr Alice',
        'minimum_credits': 1,
        'maximum_credits': 5,
        'unique_course_limit': 2,
        'times': {'MON': ['09:00-11:00']},
        'course_preferences': {'CMSC140': 8},
        'room_preferences': {'Roddy 136': 5},
        'lab_preferences': {'Linux': 7},
    }

    mgr.load_faculty([entry])
    assert 'Dr Alice' in mgr.get_faculty_names()

    f = mgr.get_faculty('Dr Alice')
    assert isinstance(f, Faculty)
    assert f.name == 'Dr Alice'
    assert f.minimum_credits == 1
    assert f.course_preferences.get('CMSC140') == 8

    # add a Faculty object directly
    bob = Faculty(name='Dr Bob', minimum_credits=0, maximum_credits=9, unique_course_limit=1)
    assert mgr.add_faculty(bob) is True
    # duplicate add should return False
    assert mgr.add_faculty(bob) is False

    # modify Bob -> rename to Bob2
    bob2 = Faculty(name='Dr Bob2', minimum_credits=0, maximum_credits=9, unique_course_limit=1)
    assert mgr.modify_faculty('Dr Bob', bob2) is True
    assert 'Dr Bob2' in mgr.get_faculty_names()

    # delete
    assert mgr.delete_faculty('Dr Bob2') is True
    assert mgr.get_faculty('Dr Bob2') is None


def test_faculty_controller_flow_and_save(tmp_path):
    mgr = FacultyManager()
    controller = FacultyController(mgr)

    data = {
        'name': 'Dr Carol',
        'minimum_credits': 0,
        'maximum_credits': 6,
        'unique_course_limit': 2,
        'times': {},
        'course_preferences': {},
        'room_preferences': {},
        'lab_preferences': {},
    }

    # add via controller
    assert controller.add_faculty(data) is True
    assert 'Dr Carol' in controller.get_faculty_names()

    # get faculty and check attributes
    f = controller.get_faculty('Dr Carol')
    assert f.name == 'Dr Carol'

    # modify via controller
    new_data = dict(data)
    new_data['minimum_credits'] = 2
    assert controller.modify_faculty('Dr Carol', new_data) is True
    f2 = controller.get_faculty('Dr Carol')
    assert f2.minimum_credits == 2

    # delete
    assert controller.delete_faculty('Dr Carol') is True
    assert not controller.faculty_exists('Dr Carol')

    # re-add and save to a temp file using controller.save_to_file
    controller.add_faculty(data)
    out = tmp_path / 'faculty_out.json'
    ok = controller.save_to_file({}, {}, str(out))
    assert ok is True
    assert out.exists()

    with open(out, 'r', encoding='utf-8') as fh:
        loaded = json.load(fh)
    # file should contain top-level 'config' and 'time_slot_config' keys
    assert 'config' in loaded
    assert 'faculty' in loaded['config']


def test_controller_rejects_invalid_faculty():
    mgr = FacultyManager()
    controller = FacultyController(mgr)

    invalid = {'name': '', 'minimum_credits': 0}
    try:
        controller.add_faculty(invalid)
        raised = False
    except Exception:
        raised = True

    assert raised is True


# --- tests merged from test_faculty_model.py ---


def test_faculty_validation():
    with pytest.raises(ValueError):
        Faculty(name="")

    with pytest.raises(ValueError):
        Faculty(name="A", minimum_credits=-1)

    with pytest.raises(ValueError):
        Faculty(name="A", minimum_credits=5, maximum_credits=3)

    with pytest.raises(ValueError):
        Faculty(name="A", unique_course_limit=0)


def test_faculty_manager_load_add_modify_delete(tmp_path):
    mgr = FacultyManager()

    valid = {
        'name': 'Dr Test',
        'minimum_credits': 1,
        'maximum_credits': 5,
        'unique_course_limit': 2,
        'times': {'MON': ['09:00-10:00']},
        'course_preferences': {'CMSC140': 5},
        'room_preferences': {'R1': 3},
        'lab_preferences': {'Linux': 4}
    }

    invalid = {'name': '', 'minimum_credits': 0}

    # load both; invalid entry should be ignored (prints warning)
    mgr.load_faculty([valid, invalid])
    assert 'Dr Test' in mgr.get_faculty_names()

    # cannot add duplicate
    dup = Faculty(name='Dr Test')
    assert mgr.add_faculty(dup) is False

    # add new faculty
    new = Faculty(name='Dr New', minimum_credits=0, maximum_credits=3)
    assert mgr.add_faculty(new) is True
    assert 'Dr New' in mgr.get_faculty_names()

    # modify faculty (rename)
    renamed = Faculty(name='Dr New2', minimum_credits=0, maximum_credits=3)
    assert mgr.modify_faculty('Dr New', renamed) is True
    assert 'Dr New2' in mgr.get_faculty_names()

    # delete
    assert mgr.delete_faculty('Dr New2') is True
    assert mgr.get_faculty('Dr New2') is None

    # to_dict contains Dr Test
    d = mgr.to_dict()
    names = [f['name'] for f in d]
    assert 'Dr Test' in names

    # save_config writes a file
    out = tmp_path / 'out.json'
    success = mgr.save_config({}, {}, str(out))
    assert success is True
    assert out.exists()
    loaded = json.loads(out.read_text(encoding='utf-8'))
    assert 'config' in loaded and 'faculty' in loaded['config']
