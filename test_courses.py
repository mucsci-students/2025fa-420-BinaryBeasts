# test_courses.py
from courses import Course, CourseManager

def test_load_and_add_course():
    config = {
        "config": {
            "rooms": ["Roddy 136", "Roddy 140", "Roddy 147"],
            "labs": ["Linux", "Mac"],
            "courses": [
                {"course_id": "CMSC 140", "credits": 4, "room": ["Roddy 136", "Roddy 140", "Roddy 147"], "lab": [], "conflicts": ["CMSC 161", "CMSC 162"], "faculty": []},
                {"course_id": "CMSC 140", "credits": 4, "room": ["Roddy 136", "Roddy 140", "Roddy 147"], "lab": [], "conflicts": ["CMSC 161", "CMSC 162"], "faculty": []},
                {"course_id": "CMSC 152", "credits": 4, "room": ["Roddy 136", "Roddy 140", "Roddy 147"], "lab": ["Mac", "Linux"], "conflicts": [], "faculty": []},
                {"course_id": "CMSC 161", "credits": 4, "room": ["Roddy 136"], "lab": ["Linux"], "conflicts": ["CMSC 140"], "faculty": ["Zoppetti"]},
                {"course_id": "CMSC 161", "credits": 4, "room": ["Roddy 136", "Roddy 140", "Roddy 147"], "lab": ["Linux"], "conflicts": [], "faculty": ["Hardy"]},
                {"course_id": "CMSC 161", "credits": 4, "room": ["Roddy 136", "Roddy 140", "Roddy 147"], "lab": ["Linux"], "conflicts": ["CMSC 140"], "faculty": []},
                {"course_id": "CMSC 162", "credits": 4, "room": ["Roddy 140"], "lab": ["Linux"], "conflicts": ["CMSC 140"], "faculty": ["Hobbs"]}
            ]
        }
    }

    mgr = CourseManager()
    mgr.load_courses(config["config"]["courses"])

    assert mgr.get_all_courses() == mgr.courses
    assert mgr.get_all_courses() is not mgr.courses

    ids = mgr.get_course_ids()
    assert "CMSC 140" in ids
    assert "CMSC 161" in ids

    new_course = Course(course_id="CMSC 170", credits=3, room=["Roddy 147"], lab=["Mac"], conflicts=[], faculty=["Doe"])
    mgr.add_course(new_course)
    assert "CMSC 170" in mgr.get_course_ids()
    assert "Doe" in mgr.faculty

    conflicts = mgr.get_conflicting_courses("CMSC 161")
    assert isinstance(conflicts, set)

def test_modify_and_delete_course():
    mgr = CourseManager()
    mgr.add_course(Course(course_id="C101", credits=4, room=["R1"], lab=["L1"], faculty=["A"], conflicts=["C999"]))
    mgr.add_course(Course(course_id="C101", credits=4, room=["R2"], lab=["L2"], faculty=["B"], conflicts=[]))
    mgr.add_course(Course(course_id="C102", credits=3, room=["R3"], lab=["L1"], faculty=["C"], conflicts=["CMCS162"]))

    assert "C102" in mgr.get_course_ids()
    assert len(mgr.get_course("C101")) == 2

    updated = Course(course_id="C101", credits=5, room=["R4"], lab=["L3"], faculty=["A", "TA1"], conflicts=["C888"])
    assert mgr.modify_course("C101", 0, updated) is True

    c0 = mgr.get_course("C101")[0]
    assert c0.credits == 5
    assert c0.room == ["R4"]
    assert "TA1" in c0.faculty
    assert c0.conflicts == ["C888"]

    assert mgr.delete_course("C101", 1) is True
    assert len(mgr.get_course("C101")) == 1

    assert mgr.delete_course("C102", 0) is True
    assert "C102" not in mgr.get_all_courses()
