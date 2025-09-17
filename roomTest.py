from room import RoomManager

def test_room_manager():
    # Sample config dictionary
    config = {
        "config": {
            "rooms": ["Room A", "Room B"],
            "courses": [
                {"course_id": "CS101", "room": ["Room A"]},
                {"course_id": "CS102", "room": ["Room B"]}
            ],
            "faculty": [
                {"name": "Dr. Smith", "room_preferences": {"Room A": 10, "Room B": 5}}
            ]
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

if __name__ == "__main__":
    test_room_manager()
