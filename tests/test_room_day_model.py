import unittest
from unittest.mock import Mock, patch
from dataclasses import dataclass
from typing import List, Dict

from src.models.room_day_model import (
    TimeBlock,
    _parse_time_str,
    schedule_to_location_blocks,
    min_max_hours,
    DAY_ORDER
)


class TestTimeBlock(unittest.TestCase):
    """Test the TimeBlock dataclass."""
    
    def test_time_block_creation(self):
        """Test basic TimeBlock creation."""
        block = TimeBlock(
            day=1,
            start=540,  # 9:00 AM
            duration=60,  # 1 hour
            course="CMSC 140",
            faculty="Hardy",
            room="Roddy 147"
        )
        
        self.assertEqual(block.day, 1)
        self.assertEqual(block.start, 540)
        self.assertEqual(block.duration, 60)
        self.assertEqual(block.course, "CMSC 140")
        self.assertEqual(block.faculty, "Hardy")
        self.assertEqual(block.room, "Roddy 147")
        self.assertFalse(block.is_lab)
        self.assertIsNone(block.lab_name)
    
    def test_time_block_with_lab(self):
        """Test TimeBlock creation with lab information."""
        block = TimeBlock(
            day=3,
            start=480,  # 8:00 AM
            duration=110,  # 1 hour 50 minutes
            course="CMSC 152",
            faculty="Smith",
            room="Roddy 136",
            is_lab=True,
            lab_name="Mac Lab"
        )
        
        self.assertTrue(block.is_lab)
        self.assertEqual(block.lab_name, "Mac Lab")


class TestParseTimeStr(unittest.TestCase):
    """Test the _parse_time_str function."""
    
    def test_parse_morning_time(self):
        """Test parsing morning time slots."""
        start, duration = _parse_time_str("09:00-09:50")
        self.assertEqual(start, 540)  # 9 * 60 = 540
        self.assertEqual(duration, 50)
    
    def test_parse_afternoon_time(self):
        """Test parsing afternoon time slots."""
        start, duration = _parse_time_str("14:00-15:50")
        self.assertEqual(start, 840)  # 14 * 60 = 840
        self.assertEqual(duration, 110)  # 1 hour 50 minutes
    
    def test_parse_cross_hour_time(self):
        """Test parsing time slots that cross hour boundaries."""
        start, duration = _parse_time_str("13:30-14:20")
        self.assertEqual(start, 810)  # 13 * 60 + 30 = 810
        self.assertEqual(duration, 50)
    
    def test_parse_zero_duration(self):
        """Test parsing time with same start and end (edge case)."""
        start, duration = _parse_time_str("10:00-10:00")
        self.assertEqual(start, 600)
        self.assertEqual(duration, 0)
    
    def test_parse_invalid_end_before_start(self):
        """Test parsing where end time is before start time."""
        start, duration = _parse_time_str("14:00-13:00")
        self.assertEqual(start, 840)
        self.assertEqual(duration, 0)  # max(0, negative_duration)


class TestScheduleToLocationBlocks(unittest.TestCase):
    """Test the schedule_to_location_blocks function."""
    
    @patch('src.models.room_day_model.parse_course_string')
    def test_empty_schedule(self, mock_parse):
        """Test with empty schedule list."""
        mock_parse.return_value = {}
        result = schedule_to_location_blocks([])
        self.assertEqual(result, {})
    
    @patch('src.models.room_day_model.parse_course_string')
    def test_single_course_no_lab(self, mock_parse):
        """Test with a single course without lab."""
        mock_parse.return_value = {
            "course_id": "CMSC 140",
            "faculty": "Hardy",
            "room": "Roddy 147",
            "lab": None,
            "time_slots": ["MON 14:00-14:50", "WED 14:00-14:50", "FRI 14:00-14:50"]
        }
        
        schedule_csv = ["CMSC 140,Hardy,Roddy 147,None,MON 14:00-14:50,WED 14:00-14:50,FRI 14:00-14:50"]
        result = schedule_to_location_blocks(schedule_csv)
        
        self.assertIn("Roddy 147", result)
        blocks = result["Roddy 147"]
        self.assertEqual(len(blocks), 3)  # MON, WED, FRI
        
        # Check Monday block
        mon_block = next(b for b in blocks if b.day == 1)
        self.assertEqual(mon_block.course, "CMSC 140")
        self.assertEqual(mon_block.faculty, "Hardy")
        self.assertEqual(mon_block.room, "Roddy 147")
        self.assertEqual(mon_block.start, 840)  # 14:00 = 14 * 60
        self.assertEqual(mon_block.duration, 50)
        self.assertFalse(mon_block.is_lab)
    
    @patch('src.models.room_day_model.parse_course_string')
    def test_course_with_lab(self, mock_parse):
        """Test with a course that has lab sessions."""
        mock_parse.return_value = {
            "course_id": "CMSC 152",
            "faculty": "Smith",
            "room": "Roddy 136",
            "lab": "Mac Lab",
            "time_slots": ["MON 09:00-09:50", "WED 09:00-10:50^", "FRI 09:00-09:50"]
        }
        
        schedule_csv = ["CMSC 152,Smith,Roddy 136,Mac Lab,MON 09:00-09:50,WED 09:00-10:50^,FRI 09:00-09:50"]
        result = schedule_to_location_blocks(schedule_csv)
        
        self.assertIn("Roddy 136", result)
        blocks = result["Roddy 136"]
        self.assertEqual(len(blocks), 3)
        
        # Check Wednesday lab block
        wed_block = next(b for b in blocks if b.day == 3)
        self.assertTrue(wed_block.is_lab)
        self.assertEqual(wed_block.lab_name, "Mac Lab")
        self.assertEqual(wed_block.duration, 110)  # 10:50 - 09:00 = 110 minutes
    
    @patch('src.models.room_day_model.parse_course_string')
    def test_multiple_courses_same_room(self, mock_parse):
        """Test multiple courses in the same room."""
        def side_effect(csv_line):
            if "CMSC 140" in csv_line:
                return {
                    "course_id": "CMSC 140",
                    "faculty": "Hardy",
                    "room": "Roddy 147",
                    "lab": None,
                    "time_slots": ["MON 14:00-14:50"]
                }
            elif "CMSC 161" in csv_line:
                return {
                    "course_id": "CMSC 161",
                    "faculty": "Jones",
                    "room": "Roddy 147",
                    "lab": None,
                    "time_slots": ["TUE 10:00-10:50"]
                }
            return {}
        
        mock_parse.side_effect = side_effect
        
        schedule_csv = [
            "CMSC 140,Hardy,Roddy 147,None,MON 14:00-14:50",
            "CMSC 161,Jones,Roddy 147,None,TUE 10:00-10:50"
        ]
        result = schedule_to_location_blocks(schedule_csv)
        
        self.assertIn("Roddy 147", result)
        blocks = result["Roddy 147"]
        self.assertEqual(len(blocks), 2)
        
        course_ids = [block.course for block in blocks]
        self.assertIn("CMSC 140", course_ids)
        self.assertIn("CMSC 161", course_ids)
    
    @patch('src.models.room_day_model.parse_course_string')
    def test_invalid_day_name(self, mock_parse):
        """Test handling of invalid day names."""
        mock_parse.return_value = {
            "course_id": "CMSC 140",
            "faculty": "Hardy",
            "room": "Roddy 147",
            "lab": None,
            "time_slots": ["INVALID 14:00-14:50", "MON 14:00-14:50"]
        }
        
        schedule_csv = ["CMSC 140,Hardy,Roddy 147,None,INVALID 14:00-14:50,MON 14:00-14:50"]
        result = schedule_to_location_blocks(schedule_csv)
        
        self.assertIn("Roddy 147", result)
        blocks = result["Roddy 147"]
        # Should only have the valid MON slot, invalid day should be skipped
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].day, 1)  # MON = 1


class TestMinMaxHours(unittest.TestCase):
    """Test the min_max_hours function."""
    
    def test_empty_blocks(self):
        """Test with empty block list."""
        min_h, max_h = min_max_hours([])
        self.assertEqual(min_h, 8)  # Default minimum
        self.assertEqual(max_h, 17)  # Default maximum
    
    def test_single_block(self):
        """Test with a single block."""
        block = TimeBlock(
            day=1, start=540, duration=60,  # 9:00-10:00
            course="CMSC 140", faculty="Hardy", room="Roddy 147"
        )
        min_h, max_h = min_max_hours([block])
        self.assertEqual(min_h, 9)
        self.assertEqual(max_h, 10)
    
    def test_multiple_blocks_different_times(self):
        """Test with multiple blocks at different times."""
        blocks = [
            TimeBlock(day=1, start=480, duration=50, course="A", faculty="X", room="R1"),  # 8:00-8:50
            TimeBlock(day=2, start=960, duration=60, course="B", faculty="Y", room="R2"),  # 16:00-17:00
            TimeBlock(day=3, start=720, duration=110, course="C", faculty="Z", room="R3")  # 12:00-13:50
        ]
        min_h, max_h = min_max_hours(blocks)
        self.assertEqual(min_h, 8)   # Earliest start hour
        self.assertEqual(max_h, 17)  # Latest end hour
    
    def test_blocks_with_padding(self):
        """Test that padding is applied correctly."""
        blocks = [
            TimeBlock(day=1, start=540, duration=60, course="A", faculty="X", room="R1")  # 9:00-10:00
        ]
        min_h, max_h = min_max_hours(blocks)
        # Should have padding around the actual times
        self.assertLessEqual(min_h, 9)
        self.assertGreaterEqual(max_h, 10)


if __name__ == '__main__':
    unittest.main()