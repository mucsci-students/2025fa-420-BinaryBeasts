"""
Basic tests for conflict management functionality.
"""

import pytest


def test_basic_conflict_detection():
    """Test basic conflict detection logic."""
    # Sample course conflicts data
    courses_with_conflicts = [
        {"course_id": "CMSC 140", "conflicts": ["CMSC 161", "CMSC 162"]},
        {"course_id": "CMSC 161", "conflicts": ["CMSC 140"]},
        {"course_id": "CMSC 162", "conflicts": ["CMSC 140"]},
        {"course_id": "CMSC 152", "conflicts": []},
    ]
    
    # Build simple conflict map
    conflicts = {}
    for course in courses_with_conflicts:
        course_id = course["course_id"]
        course_conflicts = course.get("conflicts", [])
        conflicts[course_id] = set(course_conflicts)
    
    # Test conflict detection
    assert "CMSC 161" in conflicts["CMSC 140"]
    assert "CMSC 162" in conflicts["CMSC 140"]
    assert "CMSC 140" in conflicts["CMSC 161"]
    assert len(conflicts["CMSC 152"]) == 0


def test_schedule_conflict_validation():
    """Test validating conflicts in a schedule."""
    # Sample schedule with potential conflicts
    schedule = [
        {"course_id": "CMSC 140", "time": "MON 09:00"},
        {"course_id": "CMSC 161", "time": "MON 09:00"},  # Conflict with CMSC 140
        {"course_id": "CMSC 152", "time": "TUE 10:00"},
    ]
    
    # Simple conflict rules
    conflict_rules = {
        "CMSC 140": {"CMSC 161", "CMSC 162"},
        "CMSC 161": {"CMSC 140"},
        "CMSC 162": {"CMSC 140"},
        "CMSC 152": set()
    }
    
    # Find conflicts in schedule
    conflicts_found = []
    for i, course1 in enumerate(schedule):
        for j, course2 in enumerate(schedule[i+1:], i+1):
            course1_id = course1["course_id"]
            course2_id = course2["course_id"]
            
            if course2_id in conflict_rules.get(course1_id, set()):
                conflicts_found.append((course1_id, course2_id))
    
    # Should find CMSC 140 vs CMSC 161 conflict
    assert len(conflicts_found) > 0
    assert ("CMSC 140", "CMSC 161") in conflicts_found


def test_conflict_resolution_suggestions():
    """Test basic conflict resolution logic."""
    # Schedule with conflicts
    conflicted_schedule = [
        {"course_id": "CMSC 140", "time": "MON 09:00", "room": "Room A"},
        {"course_id": "CMSC 161", "time": "MON 09:00", "room": "Room B"},  # Time conflict
    ]
    
    # Simple resolution: suggest different times
    suggested_times = ["MON 10:00", "MON 11:00", "TUE 09:00", "TUE 10:00"]
    
    # Basic resolution logic
    resolutions = []
    for course in conflicted_schedule:
        for suggested_time in suggested_times:
            if suggested_time != course["time"]:
                resolution = {
                    "course_id": course["course_id"],
                    "original_time": course["time"],
                    "suggested_time": suggested_time
                }
                resolutions.append(resolution)
                break  # Take first available alternative
    
    assert len(resolutions) >= 1
    assert resolutions[0]["suggested_time"] != resolutions[0]["original_time"]
