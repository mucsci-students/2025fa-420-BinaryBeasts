from src.models.course_model import Course, CourseManager

def test1():
    # Sample config
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
            ],
        }
    }

    # Build manager and load courses
    mgr = CourseManager()
    mgr.load_courses(config["config"]["courses"])

    # Initial checks / prints
    print("Initial course IDs:", mgr.get_course_ids())
    print("Initial rooms:", mgr.rooms)
    print("Initial labs:", mgr.labs)
    print("Initial faculty:", mgr.faculty)

    # get_all_courses returns the actual dict (identity)
    all_courses = mgr.get_all_courses()
    assert all_courses == mgr.courses  # compare contents
    # or, if you want to prove it's a different object:
    assert all_courses is not mgr.courses

    # Basic existence checks
    assert "CMSC 140" in mgr.get_course_ids()
    assert "CMSC 161" in mgr.get_course_ids()

    # Add a new course
    new_course = Course(course_id="CMSC 170", credits=3, room=["Roddy 147"], lab=["Mac"], conflicts=[], faculty=["Doe"])
    mgr.add_course(new_course)
    assert "CMSC 170" in mgr.get_course_ids()
    assert "Doe" in mgr.faculty    # resource sets updated


    print("After adding CMSC 170 --> courses:", mgr.get_course_ids(), mgr.rooms, "\nlabs:", mgr.labs, "faculty:", mgr.faculty)


    # Conflicts helper (local, no external manager)
    conflicts = mgr.get_conflicting_courses("CMSC 161")
    print("Conflicts for CMSC 161:", conflicts)
    conflict = mgr.get_conflicting_courses("CMSC 140")
    print("Conflict for CMSC 140:", conflict)
    # May or may not include conflicts depending on which instance is first; just ensure set type
    assert isinstance(conflicts, set)


def test2():

    mgr = CourseManager()
    mgr.add_course(Course(course_id="C101", credits=4, room=["R1"], lab=["L1"], faculty=["A"], conflicts=["C999"]))
    mgr.add_course(Course(course_id="C101", credits=4, room=["R2"], lab=["L2"], faculty=["B"], conflicts=[]))
    mgr.add_course(Course(course_id="C102", credits=3, room=["R3"], lab=["L1"], faculty=["C"], conflicts=["CMCS162"]))

    assert "C102" in mgr.get_course_ids()
    print("New rooms:", mgr.rooms)

    print("Before modify C101[0]--> courses:", mgr.get_course_ids(), "rooms: ", mgr.rooms, "labs:", mgr.labs, "faculty:", mgr.faculty)
    assert len(mgr.get_course("C101")) == 2

    # Modify first instance of C101
    # Create a new Course object with the updated data
    updated = Course(
        course_id="C101",
        credits=5,
        room=["R4"],  # new room
        lab=["L3"],  # new lab
        faculty=["A", "TA1"],  # add TA1
        conflicts=["C888"]  # replace old conflicts
    )

    # Call modify_course to replace the old instance with this new one
    modify = mgr.modify_course("C101", 0, updated)
    assert modify is True
    # Get the first C101 course after modification
    c0 = mgr.get_course("C101")[0]
    # Verify all the fields were actually updated
    assert c0.credits == 5
    assert c0.room == ["R4"]
    assert "TA1" in c0.faculty
    assert c0.conflicts == ["C888"]
    print("After modify C101[0] --> courses:", mgr.get_course_ids(), mgr.rooms, "labs:", mgr.labs, "faculty:", mgr.faculty)

    # Delete second instance of C101
    assert mgr.delete_course("C101", 1) is True
    assert len(mgr.get_course("C101")) == 1

    # Delete only instance of C102 (should remove key)
    assert mgr.delete_course("C102", 0) is True
    assert "C102" not in mgr.get_all_courses()

    # Resource sets should reflect current state
    print("After delete C101[1] and C102 --> courses:", mgr.get_course_ids(), mgr.rooms, "labs:", mgr.labs, "faculty:", mgr.faculty)


if __name__ == "__main__":
    test1()
    print()
    test2()
    print("\n passed ")
