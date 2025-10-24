"""
Basic tests for CSV output functionality.
"""

import json
import pytest
import tempfile
import csv


def test_csv_output_format():
    """Test CSV output formatting."""
    # Sample schedule data
    schedule_data = [
        {
            "schedule_id": 1,
            "courses": [
                {
                    "course_id": "CMSC 140",
                    "day": "MON",
                    "time": "09:00",
                    "duration": 110,
                    "room": "Roddy 136",
                    "lab": "",
                    "faculty": "Dr. Smith"
                }
            ]
        }
    ]
    
    # Convert to CSV format
    csv_rows = []
    csv_rows.append(["Schedule", "Course", "Day", "Time", "Duration", "Room", "Lab", "Faculty"])
    
    for schedule in schedule_data:
        schedule_id = schedule["schedule_id"]
        for course in schedule["courses"]:
            csv_rows.append([
                schedule_id,
                course["course_id"],
                course["day"],
                course["time"],
                course["duration"],
                course["room"],
                course["lab"],
                course["faculty"]
            ])
    
    # Verify CSV structure
    assert len(csv_rows) == 2  # Header + 1 data row
    assert csv_rows[0] == ["Schedule", "Course", "Day", "Time", "Duration", "Room", "Lab", "Faculty"]
    assert csv_rows[1][1] == "CMSC 140"  # Course ID


def test_csv_file_writing(tmp_path):
    """Test writing CSV data to file."""
    # Sample data
    csv_data = [
        ["Schedule", "Course", "Day", "Time"],
        [1, "TEST 101", "MON", "09:00"],
        [1, "TEST 102", "TUE", "10:00"]
    ]
    
    # Write to temp file
    csv_file = tmp_path / "test_output.csv"
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(csv_data)
    
    # Verify file was created and has correct content
    assert csv_file.exists()
    
    # Read back and verify
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    assert len(rows) == 3
    assert rows[0] == ["Schedule", "Course", "Day", "Time"]
    assert rows[1] == ["1", "TEST 101", "MON", "09:00"]


def test_json_to_csv_conversion():
    """Test converting JSON schedule data to CSV format."""
    # JSON schedule data
    json_schedules = [
        {
            "schedule_id": 1,
            "courses": [
                {"course_id": "MATH 101", "time": "MON 09:00", "room": "Room A"},
                {"course_id": "ENG 101", "time": "TUE 10:00", "room": "Room B"}
            ]
        }
    ]
    
    # Convert to CSV format
    csv_output = []
    csv_output.append(["Schedule", "Course", "Time", "Room"])
    
    for schedule in json_schedules:
        schedule_id = schedule["schedule_id"]
        for course in schedule["courses"]:
            csv_output.append([
                schedule_id,
                course["course_id"],
                course["time"],
                course["room"]
            ])
    
    # Verify conversion
    assert len(csv_output) == 3  # Header + 2 courses
    assert csv_output[1][1] == "MATH 101"
    assert csv_output[2][1] == "ENG 101"