import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from PyQt5.QtWidgets import QApplication

from src.models.room_day_model import TimeBlock, schedule_to_location_blocks
from src.controllers.schedules_controller import generate_controller
from src.views.gui.schedule_visualization_view import RoomPanel, _key_color


class TestScheduleVisualizationIntegration(unittest.TestCase):
    """Integration tests for the complete schedule visualization system."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for testing GUI components."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_csv_schedule = [
            "CMSC 140,Hardy,Roddy 147,None,MON 14:00-14:50,WED 14:00-14:50,FRI 14:00-14:50",
            "CMSC 152,Smith,Roddy 136,Mac Lab,MON 09:00-09:50,WED 09:00-10:50^,FRI 09:00-09:50",
            "CMSC 161,Jones,Roddy 147,Linux,TUE 10:00-10:50,THU 10:00-11:50^"
        ]
    
    @patch('src.models.room_day_model.parse_course_string')
    def test_end_to_end_schedule_visualization(self, mock_parse):
        """Test complete flow from CSV schedule to room panels."""
        
        def parse_side_effect(csv_line):
            if "CMSC 140" in csv_line:
                return {
                    "course_id": "CMSC 140",
                    "faculty": "Hardy", 
                    "room": "Roddy 147",
                    "lab": None,
                    "time_slots": ["MON 14:00-14:50", "WED 14:00-14:50", "FRI 14:00-14:50"]
                }
            elif "CMSC 152" in csv_line:
                return {
                    "course_id": "CMSC 152",
                    "faculty": "Smith",
                    "room": "Roddy 136", 
                    "lab": "Mac Lab",
                    "time_slots": ["MON 09:00-09:50", "WED 09:00-10:50^", "FRI 09:00-09:50"]
                }
            elif "CMSC 161" in csv_line:
                return {
                    "course_id": "CMSC 161",
                    "faculty": "Jones",
                    "room": "Roddy 147",
                    "lab": "Linux", 
                    "time_slots": ["TUE 10:00-10:50", "THU 10:00-11:50^"]
                }
            return {}
        
        mock_parse.side_effect = parse_side_effect
        
        # Step 1: Convert CSV schedule to location blocks
        location_blocks = schedule_to_location_blocks(self.sample_csv_schedule)
        
        # Step 2: Verify room grouping
        self.assertIn("Roddy 147", location_blocks)
        self.assertIn("Roddy 136", location_blocks)
        
        # Roddy 147 should have blocks from CMSC 140 and CMSC 161
        roddy147_blocks = location_blocks["Roddy 147"]
        course_ids = {block.course for block in roddy147_blocks}
        self.assertIn("CMSC 140", course_ids)
        self.assertIn("CMSC 161", course_ids)
        
        # Step 3: Create room panels
        roddy147_panel = RoomPanel("Roddy 147", roddy147_blocks)
        roddy136_panel = RoomPanel("Roddy 136", location_blocks["Roddy 136"])
        
        # Step 4: Verify panels are properly constructed
        self.assertEqual(roddy147_panel.title, "Roddy 147")
        self.assertGreater(len(roddy147_panel.blocks), 0)
        
        self.assertEqual(roddy136_panel.title, "Roddy 136")
        self.assertGreater(len(roddy136_panel.blocks), 0)
    
    def test_controller_integration_with_visualization(self):
        """Test integration between controller and visualization components."""
        
        # Create mock course objects
        mock_course1 = Mock()
        mock_course1.as_csv.return_value = "CMSC 140,Hardy,Roddy 147,None,MON 14:00-14:50"
        
        mock_course2 = Mock()
        mock_course2.as_csv.return_value = "CMSC 152,Smith,Roddy 136,Mac Lab,WED 09:00-10:50^"
        
        # Create schedules and controller
        schedules = [[mock_course1, mock_course2]]
        controller = generate_controller(schedules)
        
        # Get CSV strings from controller
        csv_strings = controller.get_current_schedule_strings()
        self.assertEqual(len(csv_strings), 2)
        
        # These strings could then be passed to schedule_to_location_blocks
        # (We don't test the full integration here to avoid mocking complexity)
        self.assertIn("CMSC 140", csv_strings[0])
        self.assertIn("CMSC 152", csv_strings[1])
    
    @patch('src.models.room_day_model.parse_course_string')
    def test_lab_visualization_integration(self, mock_parse):
        """Test that lab sessions are properly integrated in visualization."""
        
        mock_parse.return_value = {
            "course_id": "CMSC 152",
            "faculty": "Smith",
            "room": "Roddy 136",
            "lab": "Mac Lab",
            "time_slots": ["MON 09:00-09:50", "WED 09:00-10:50^", "FRI 09:00-09:50"]
        }
        
        csv_schedule = ["CMSC 152,Smith,Roddy 136,Mac Lab,MON 09:00-09:50,WED 09:00-10:50^,FRI 09:00-09:50"]
        
        # Convert to blocks
        location_blocks = schedule_to_location_blocks(csv_schedule)
        blocks = location_blocks["Roddy 136"]
        
        # Create panel
        panel = RoomPanel("Roddy 136", blocks)
        
        # Verify lab blocks are included
        lab_blocks = [b for b in panel.blocks if b.is_lab]
        regular_blocks = [b for b in panel.blocks if not b.is_lab]
        
        self.assertEqual(len(lab_blocks), 1)  # Wednesday lab
        self.assertEqual(len(regular_blocks), 2)  # Monday and Friday lectures
        
        # Verify lab block properties
        lab_block = lab_blocks[0]
        self.assertEqual(lab_block.day, 3)  # Wednesday
        self.assertEqual(lab_block.duration, 110)  # 10:50 - 09:00 = 110 minutes
        self.assertEqual(lab_block.lab_name, "Mac Lab")
    
    def test_color_consistency_across_components(self):
        """Test that color generation is consistent across different uses."""
        
        course_id = "CMSC 140"
        
        # Generate colors multiple times
        color1 = _key_color(course_id)
        color2 = _key_color(course_id)
        color3 = _key_color(course_id)
        
        # All should be identical
        self.assertEqual(color1.hue(), color2.hue())
        self.assertEqual(color2.hue(), color3.hue())
        self.assertEqual(color1.saturation(), color2.saturation())
        self.assertEqual(color2.saturation(), color3.saturation())
    
    @patch('src.models.room_day_model.parse_course_string')
    def test_multi_room_schedule_visualization(self, mock_parse):
        """Test visualization of schedules across multiple rooms."""
        
        def parse_side_effect(csv_line):
            if "Room1" in csv_line:
                return {
                    "course_id": "CMSC 140",
                    "faculty": "Prof A",
                    "room": "Room1", 
                    "lab": None,
                    "time_slots": ["MON 10:00-10:50"]
                }
            elif "Room2" in csv_line:
                return {
                    "course_id": "CMSC 161", 
                    "faculty": "Prof B",
                    "room": "Room2",
                    "lab": None,
                    "time_slots": ["TUE 11:00-11:50"]
                }
            return {}
        
        mock_parse.side_effect = parse_side_effect
        
        csv_schedule = [
            "CMSC 140,Prof A,Room1,None,MON 10:00-10:50",
            "CMSC 161,Prof B,Room2,None,TUE 11:00-11:50"
        ]
        
        # Convert to location blocks
        location_blocks = schedule_to_location_blocks(csv_schedule)
        
        # Should have separate room groupings
        self.assertEqual(len(location_blocks), 2)
        self.assertIn("Room1", location_blocks)
        self.assertIn("Room2", location_blocks)
        
        # Create panels for each room
        panels = {}
        for room_name, blocks in location_blocks.items():
            panels[room_name] = RoomPanel(room_name, blocks)
        
        # Verify each panel
        self.assertEqual(len(panels), 2)
        self.assertIn("Room1", panels)
        self.assertIn("Room2", panels)
        
        # Each panel should have exactly one block
        self.assertEqual(len(panels["Room1"].blocks), 1)
        self.assertEqual(len(panels["Room2"].blocks), 1)
    
    def test_empty_schedule_handling(self):
        """Test handling of empty schedules throughout the system."""
        
        # Empty CSV schedule
        empty_schedule = []
        
        # Should produce empty location blocks
        location_blocks = schedule_to_location_blocks(empty_schedule)
        self.assertEqual(location_blocks, {})
        
        # Empty controller
        empty_controller = generate_controller([])
        csv_strings = empty_controller.get_current_schedule_strings()
        self.assertEqual(csv_strings, [])
        
        # Empty room panel
        empty_panel = RoomPanel("Empty Room", [])
        self.assertEqual(len(empty_panel.blocks), 0)
        self.assertEqual(empty_panel.title, "Empty Room")
    
    @patch('src.models.room_day_model.parse_course_string')
    def test_schedule_with_conflicts_visualization(self, mock_parse):
        """Test visualization when multiple courses use the same room/time."""
        
        mock_parse.side_effect = [
            {
                "course_id": "CMSC 140",
                "faculty": "Prof A",
                "room": "Conflict Room",
                "lab": None,
                "time_slots": ["MON 10:00-10:50"]
            },
            {
                "course_id": "CMSC 161", 
                "faculty": "Prof B",
                "room": "Conflict Room",
                "lab": None,
                "time_slots": ["MON 10:00-10:50"]  # Same time!
            }
        ]
        
        csv_schedule = [
            "CMSC 140,Prof A,Conflict Room,None,MON 10:00-10:50",
            "CMSC 161,Prof B,Conflict Room,None,MON 10:00-10:50"
        ]
        
        location_blocks = schedule_to_location_blocks(csv_schedule)
        
        # Should still create blocks (visualization doesn't check for conflicts)
        self.assertIn("Conflict Room", location_blocks)
        blocks = location_blocks["Conflict Room"]
        self.assertEqual(len(blocks), 2)
        
        # Both blocks should be for Monday at the same time
        for block in blocks:
            self.assertEqual(block.day, 1)  # Monday
            self.assertEqual(block.start, 600)  # 10:00 AM


class TestScheduleVisualizationErrorHandling(unittest.TestCase):
    """Test error handling in schedule visualization components."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for testing GUI components."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    @patch('src.models.room_day_model.parse_course_string')
    def test_parse_error_handling(self, mock_parse):
        """Test handling of parse errors in schedule conversion."""
        
        # Mock parse function to return empty dict for some courses
        mock_parse.side_effect = [
            {},  # Empty result (parse error)
            {
                "course_id": "CMSC 161",
                "faculty": "Prof B", 
                "room": "Room1",
                "lab": None,
                "time_slots": ["TUE 10:00-10:50"]
            }
        ]
        
        csv_schedule = [
            "INVALID_CSV_LINE",
            "CMSC 161,Prof B,Room1,None,TUE 10:00-10:50"
        ]
        
        location_blocks = schedule_to_location_blocks(csv_schedule)
        
        # Should only have blocks from the valid course
        self.assertEqual(len(location_blocks), 1)
        self.assertIn("Room1", location_blocks) 
        self.assertEqual(len(location_blocks["Room1"]), 1)
    
    def test_invalid_time_format_handling(self):
        """Test handling of invalid time formats in TimeBlock creation."""
        
        # This would normally cause issues in _parse_time_str
        # but the function should handle it gracefully
        from src.models.room_day_model import _parse_time_str
        
        # Test various invalid formats
        try:
            start, duration = _parse_time_str("INVALID")
            # Should not raise exception, but may return unexpected values
        except:
            pass  # Expected to potentially fail, but shouldn't crash the system
        
        try:
            start, duration = _parse_time_str("25:00-26:00")  # Invalid hours
            # Should handle gracefully
        except:
            pass


if __name__ == '__main__':
    unittest.main()