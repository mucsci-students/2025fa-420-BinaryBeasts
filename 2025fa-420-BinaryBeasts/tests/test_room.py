import os, sys
# Ensure project root is on path so `import src...` works
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Add sibling scheduler/src to path if scheduler isn't installed
try:
    from scheduler.config import SchedulerConfig  # type: ignore
except Exception:
    SCHEDULER_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "scheduler", "src"))
    if SCHEDULER_SRC not in sys.path:
        sys.path.insert(0, SCHEDULER_SRC)
    from scheduler.config import SchedulerConfig  # type: ignore

from src.room import RoomManager
from scheduler.config import SchedulerConfig


def make_scheduler_config(data: dict) -> SchedulerConfig:
    return SchedulerConfig.model_validate(data)


def test_room_manager():
    # Minimal valid scheduler config matching scheduler models
    sched_data = {
        "rooms": ["Room A", "Room B"],
        "labs": [],
        "courses": [
            {
                "course_id": "CS101",
                "credits": 3,
                "room": ["Room A"],
                "lab": [],
                "conflicts": [],
                "faculty": ["Dr. Smith"],
            },
            {
                "course_id": "CS102",
                "credits": 3,
                "room": ["Room B"],
                "lab": [],
                "conflicts": [],
                "faculty": ["Dr. Smith"],
            },
        ],
        "faculty": [
            {
                "name": "Dr. Smith",
                "maximum_credits": 12,
                "minimum_credits": 3,
                "unique_course_limit": 3,
                "times": {"MON": ["10:00-12:00"]},
                "course_preferences": {"CS101": 5, "CS102": 5},
                "room_preferences": {"Room A": 10, "Room B": 5},
                "lab_preferences": {},
            }
        ],
    }
    sched = make_scheduler_config(sched_data)
    manager = RoomManager(sched)

    # Add
    assert manager.add_room("Room C") is True
    assert manager.add_room("Room A") is False

    # Delete
    assert manager.delete_room("Room B") is True
    assert manager.delete_room("Room X") is False

    # Rename
    assert manager.edit_room("Room A", "Room D") is True
    assert manager.edit_room("Room X", "Room Y") is False
    assert manager.edit_room("Room D", "Room C") is False

    # Validate references updated via a dict dump
    dump = manager.to_combined_dict()["config"]
    # Rooms now should be ["Room C", "Room D"] in some order
    assert set(dump["rooms"]) == {"Room C", "Room D"}
    # Course rooms: CS101 now references Room D; CS102 had Room B removed
    c_by_id = {c["course_id"]: c for c in dump["courses"]}
    assert c_by_id["CS101"]["room"] == ["Room D"]
    assert c_by_id["CS102"]["room"] == []
    # Faculty room preferences updated key from Room A -> Room D; Room B removed
    prefs = dump["faculty"][0]["room_preferences"]
    assert "Room B" not in prefs
    assert "Room D" in prefs


def test_set_rooms():
    sched_data = {
        "rooms": ["R1", "R2", "R3"],
        "labs": [],
        "courses": [
            {
                "course_id": "C1",
                "credits": 3,
                "room": ["R1", "R2"],
                "lab": [],
                "conflicts": [],
                "faculty": ["F1"],
            },
            {
                "course_id": "C2",
                "credits": 3,
                "room": ["R3"],
                "lab": [],
                "conflicts": [],
                "faculty": ["F1"],
            },
        ],
        "faculty": [
            {
                "name": "F1",
                "maximum_credits": 12,
                "minimum_credits": 3,
                "unique_course_limit": 3,
                "times": {"MON": ["10:00-12:00"]},
                "course_preferences": {"C1": 5, "C2": 5},
                "room_preferences": {"R1": 5, "R2": 3, "R3": 1},
                "lab_preferences": {},
            }
        ],
    }
    sched = make_scheduler_config(sched_data)
    manager = RoomManager(sched)

    report = manager.set_rooms(["R2", "R4"])  # R1,R3 removed; R4 added
    assert report["added"] == ["R4"]
    assert sorted(report["removed"]) == ["R1", "R3"]

    # Rooms list updated
    assert set(manager.get_rooms()) == {"R2", "R4"}

    dump = manager.to_combined_dict()["config"]
    # Course references: C1 should keep only R2, C2 loses its room (becomes empty list)
    c_by_id = {c["course_id"]: c for c in dump["courses"]}
    assert c_by_id["C1"]["room"] == ["R2"]
    assert c_by_id["C2"]["room"] == []

    # Faculty preferences: removed keys gone, R2 preserved
    prefs = dump["faculty"][0]["room_preferences"]
    assert "R1" not in prefs and "R3" not in prefs
    assert prefs.get("R2") == 3
