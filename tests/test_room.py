from room import RoomManager


def test_room_manager():
    # Sample config dictionary
    config = {
        "config": {
            "rooms": ["Room A", "Room B"],
            "courses": [
                {"course_id": "CS101", "room": ["Room A"]},
                {"course_id": "CS102", "room": ["Room B"]},
            ],
            "faculty": [
                {"name": "Dr. Smith", "room_preferences": {"Room A": 10, "Room B": 5}}
            ],
        }
    }
    manager = RoomManager(config)

    print("Initial rooms:", manager.get_rooms())
    assert manager.add_room("Room C") == True
    assert manager.add_room("Room A") == False  # Already exists
    print("Rooms after adding Room C:", manager.get_rooms())

    assert manager.delete_room("Room B") == True
    assert manager.delete_room("Room X") == False  # Does not exist
    print("Rooms after deleting Room B:", manager.get_rooms())

    assert manager.edit_room("Room A", "Room D") == True
    assert manager.edit_room("Room X", "Room Y") == False  # Old name does not exist
    assert manager.edit_room("Room D", "Room C") == False  # New name already exists
    print("Rooms after renaming Room A to Room D:", manager.get_rooms())

    # Check that course and faculty references are updated
    print("Courses after edit:", config["config"]["courses"])
    print("Faculty after edit:", config["config"]["faculty"])


def test_set_rooms():
    config = {
        "config": {
            "rooms": ["R1", "R2", "R3"],
            "courses": [
                {"course_id": "C1", "room": ["R1", "R2"]},
                {"course_id": "C2", "room": ["R3"]},
            ],
            "faculty": [
                {"name": "F1", "room_preferences": {"R1": 5, "R2": 3, "R3": 1}}
            ],
        }
    }
    manager = RoomManager(config)

    report = manager.set_rooms(["R2", "R4"])  # R1,R3 removed; R4 added
    assert report["added"] == ["R4"]
    assert sorted(report["removed"]) == ["R1", "R3"]

    # Rooms list updated
    assert manager.get_rooms() == ["R2", "R4"]

    # Course references: C1 should keep only R2, C2 loses its room (becomes empty list)
    assert config["config"]["courses"][0]["room"] == ["R2"]
    assert config["config"]["courses"][1]["room"] == []

    # Faculty preferences: removed keys gone
    prefs = config["config"]["faculty"][0]["room_preferences"]
    assert "R1" not in prefs and "R3" not in prefs
    assert prefs.get("R2") == 3


if __name__ == "__main__":
    test_room_manager()
    test_set_rooms()

if __name__ == "__main__":
    test_room_manager()
