from __future__ import annotations

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from src.views.cli.schedules_view import parse_course_string


DAY_ORDER = {"MON": 1, "TUE": 2, "WED": 3, "THU": 4, "FRI": 5}


@dataclass
class TimeBlock:
    day: int           # 1..5
    start: int         # minutes from midnight
    duration: int      # minutes
    course: str
    faculty: str
    room: str          # the location label for the panel (lecture room)
    is_lab: bool = False
    lab_name: Optional[str] = None  # original lab location if present


def _parse_time_str(time_str: str) -> Tuple[int, int]:
    """Parse HH:MM-HH:MM into (start_min, duration_min)."""
    start_str, end_str = time_str.split("-")
    sh, sm = [int(x) for x in start_str.split(":")]
    eh, em = [int(x) for x in end_str.split(":")]
    start = sh * 60 + sm
    end = eh * 60 + em
    return start, max(0, end - start)


def schedule_to_location_blocks(schedule_csv: List[str]) -> Dict[str, List[TimeBlock]]:
    """Convert a schedule of CSV course strings into room -> list of TimeBlock.

    Rooms and labs are combined: all time slots (including lab-marked '^')
    are shown under the course's lecture room panel. Each block indicates
    whether it's a lab via `is_lab`, and preserves the original lab name.
    """
    locations: Dict[str, List[TimeBlock]] = {}

    for csv_line in schedule_csv:
        course = parse_course_string(csv_line)
        if not course:
            continue

        course_id = course["course_id"]
        faculty = course["faculty"]
        room = course["room"]
        lab = course.get("lab")

    # All slots -> room panel, mark lab slots
        for slot in course["time_slots"]:
            is_lab = "^" in slot
            day_time = slot.replace("^", "")
            parts = day_time.split(" ", 1)
            if len(parts) != 2:
                continue
            day_code, time_str = parts[0].strip(), parts[1].strip()
            day = DAY_ORDER.get(day_code)
            if not day:
                continue
            start, dur = _parse_time_str(time_str)
            # Always draw under the lecture room panel; mark labs in the block
            if room and room.lower() != "none":
                locations.setdefault(room, []).append(
                    TimeBlock(
                        day=day,
                        start=start,
                        duration=dur,
                        course=course_id,
                        faculty=faculty,
                        room=room,
                        is_lab=is_lab,
                        lab_name=(lab if (is_lab and lab and lab.lower() != "none") else None),
                    )
                )

    return locations


def min_max_hours(blocks: List[TimeBlock]) -> Tuple[int, int]:
    """Compute [minHour, maxHour] integer hours range for the given blocks."""
    if not blocks:
        return 8, 17
    min_h = 24
    max_h = 0
    for b in blocks:
        s_h = b.start // 60
        e_h = (b.start + b.duration + 59) // 60
        min_h = min(min_h, s_h)
        max_h = max(max_h, e_h)
    if min_h == 24 or max_h == 0:
        return 8, 17
    return min_h, max_h
