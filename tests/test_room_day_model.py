import pytest

from src.models.room_day_model import _parse_time_str, schedule_to_location_blocks, min_max_hours, TimeBlock


def test_parse_time_str_basic():
    start, dur = _parse_time_str("09:00-10:30")
    assert start == 9 * 60
    assert dur == 90


def test_schedule_to_location_blocks_lab_and_room():
    # CSV format: course_id,faculty,room,lab,time_slots...
    csv = "CMSC101,Dr Smith,RoomA,LabA,MON 09:00-09:50^"
    locs = schedule_to_location_blocks([csv])
    assert "RoomA" in locs
    blocks = locs["RoomA"]
    assert len(blocks) == 1
    b = blocks[0]
    assert isinstance(b, TimeBlock)
    assert b.course == "CMSC101"
    assert b.faculty == "Dr Smith"
    assert b.is_lab is True
    # lab_name should come from the lab field (LabA)
    assert b.lab_name == "LabA"


def test_min_max_hours_empty_and_values():
    assert min_max_hours([]) == (8, 17)

    b1 = TimeBlock(day=1, start=8 * 60, duration=50, course="A", faculty="X", room="R")
    b2 = TimeBlock(day=2, start=13 * 60 + 30, duration=80, course="B", faculty="Y", room="R")
    mn, mx = min_max_hours([b1, b2])
    assert mn <= 8
    assert mx >= 15  # 13:30 + 80 -> ends after 14:50 -> hour 15
