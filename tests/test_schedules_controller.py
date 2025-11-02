import unittest
from unittest.mock import Mock, MagicMock, patch
import json

from src.controllers.schedules_controller import generate_controller


class TestGenerateController(unittest.TestCase):
    """Test the generate_controller class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock schedule objects with as_csv method
        self.mock_course1 = Mock()
        self.mock_course1.as_csv.return_value = "CMSC 140,Hardy,Roddy 147,None,MON 14:00-14:50"
        
        self.mock_course2 = Mock()
        self.mock_course2.as_csv.return_value = "CMSC 161,Smith,Roddy 136,Mac Lab,TUE 10:00-11:50^"
        
        self.mock_course3 = Mock()
        self.mock_course3.as_csv.return_value = "CMSC 152,Jones,Roddy 140,Linux,WED 09:00-09:50"
        
        # Create mock schedules
        self.schedule1 = [self.mock_course1, self.mock_course2]
        self.schedule2 = [self.mock_course3]
        self.schedules = [self.schedule1, self.schedule2]
    
    def test_controller_initialization(self):
        """Test controller initialization."""
        controller = generate_controller(self.schedules)
        
        self.assertEqual(controller.schedules, self.schedules)
        self.assertEqual(controller.index, 0)
    
    def test_next_schedule(self):
        """Test next_schedule method."""
        controller = generate_controller(self.schedules)
        
        # Initially at index 0
        self.assertEqual(controller.index, 0)
        
        # Move to next schedule
        controller.next_schedule()
        self.assertEqual(controller.index, 1)
        
        # Move to next schedule (should wrap around)
        controller.next_schedule()
        self.assertEqual(controller.index, 0)
    
    def test_previous_schedule(self):
        """Test previous_schedule method."""
        controller = generate_controller(self.schedules)
        
        # Initially at index 0
        self.assertEqual(controller.index, 0)
        
        # Move to previous schedule (should wrap to last)
        controller.previous_schedule()
        self.assertEqual(controller.index, 1)
        
        # Move to previous schedule again
        controller.previous_schedule()
        self.assertEqual(controller.index, 0)
    
    def test_get_current_schedule_strings_first_schedule(self):
        """Test getting CSV strings for the first schedule."""
        controller = generate_controller(self.schedules)
        
        strings = controller.get_current_schedule_strings()
        
        expected = [
            "CMSC 140,Hardy,Roddy 147,None,MON 14:00-14:50",
            "CMSC 161,Smith,Roddy 136,Mac Lab,TUE 10:00-11:50^"
        ]
        self.assertEqual(strings, expected)
    
    def test_get_current_schedule_strings_second_schedule(self):
        """Test getting CSV strings for the second schedule."""
        controller = generate_controller(self.schedules)
        controller.next_schedule()  # Move to index 1
        
        strings = controller.get_current_schedule_strings()
        
        expected = ["CMSC 152,Jones,Roddy 140,Linux,WED 09:00-09:50"]
        self.assertEqual(strings, expected)
    
    def test_get_current_schedule_strings_empty_schedules(self):
        """Test getting CSV strings when schedules list is empty."""
        controller = generate_controller([])
        
        strings = controller.get_current_schedule_strings()
        
        self.assertEqual(strings, [])
    
    def test_get_current_schedule_strings_invalid_index(self):
        """Test getting CSV strings with invalid index."""
        controller = generate_controller(self.schedules)
        controller.index = 999  # Set invalid index
        
        strings = controller.get_current_schedule_strings()
        
        self.assertEqual(strings, [])
    
    def test_get_current_schedule_strings_with_none_course(self):
        """Test handling of None courses in schedule."""
        schedule_with_none = [self.mock_course1, None, self.mock_course2]
        controller = generate_controller([schedule_with_none])
        
        strings = controller.get_current_schedule_strings()
        
        # Should skip None and only include valid courses
        expected = [
            "CMSC 140,Hardy,Roddy 147,None,MON 14:00-14:50",
            "CMSC 161,Smith,Roddy 136,Mac Lab,TUE 10:00-11:50^"
        ]
        self.assertEqual(strings, expected)
    
    def test_get_current_schedule_strings_as_csv_exception(self):
        """Test handling of as_csv method throwing exception."""
        mock_course_error = Mock()
        mock_course_error.as_csv.side_effect = Exception("CSV error")
        
        schedule_with_error = [self.mock_course1, mock_course_error, self.mock_course2]
        controller = generate_controller([schedule_with_error])
        
        strings = controller.get_current_schedule_strings()
        
        # Should skip the problematic course and continue with others
        expected = [
            "CMSC 140,Hardy,Roddy 147,None,MON 14:00-14:50",
            "CMSC 161,Smith,Roddy 136,Mac Lab,TUE 10:00-11:50^"
        ]
        self.assertEqual(strings, expected)
    
    def test_schedule_navigation_full_cycle(self):
        """Test complete navigation cycle through schedules."""
        controller = generate_controller(self.schedules)
        
        # Start at 0
        self.assertEqual(controller.index, 0)
        
        # Forward navigation
        controller.next_schedule()
        self.assertEqual(controller.index, 1)
        
        controller.next_schedule()
        self.assertEqual(controller.index, 0)  # Wrapped around
        
        # Backward navigation
        controller.previous_schedule()
        self.assertEqual(controller.index, 1)  # Wrapped to last
        
        controller.previous_schedule()
        self.assertEqual(controller.index, 0)
    
    def test_single_schedule_navigation(self):
        """Test navigation with only one schedule."""
        single_schedule = [self.schedule1]
        controller = generate_controller(single_schedule)
        
        # Should stay at index 0
        self.assertEqual(controller.index, 0)
        
        controller.next_schedule()
        self.assertEqual(controller.index, 0)
        
        controller.previous_schedule()
        self.assertEqual(controller.index, 0)


class TestGenerateControllerIntegration(unittest.TestCase):
    """Integration tests for generate_controller with real data structures."""
    
    @patch('src.controllers.schedules_controller.schedules_view')
    def test_with_mock_schedules_view(self, mock_schedules_view):
        """Test controller with mocked schedules_view functions."""
        # Set up mock functions
        mock_schedules_view.display_schedule_basic = Mock()
        mock_schedules_view.display_schedule_by_room = Mock()
        mock_schedules_view.display_schedule_by_faculty = Mock()
        
        # Create controller
        schedules = [[Mock(), Mock()], [Mock()]]
        controller = generate_controller(schedules)
        
        # Test that controller can be created and used
        self.assertEqual(len(controller.schedules), 2)
        self.assertEqual(controller.index, 0)
        
        # Test navigation
        controller.next_schedule()
        self.assertEqual(controller.index, 1)


class TestGenerateControllerEdgeCases(unittest.TestCase):
    """Test edge cases for generate_controller."""
    
    def test_negative_index_initialization(self):
        """Test controller behavior with manually set negative index."""
        controller = generate_controller([[Mock()]])
        controller.index = -5
        
        strings = controller.get_current_schedule_strings()
        self.assertEqual(strings, [])
    
    def test_large_positive_index(self):
        """Test controller behavior with manually set large positive index."""
        controller = generate_controller([[Mock()]])
        controller.index = 1000
        
        strings = controller.get_current_schedule_strings()
        self.assertEqual(strings, [])
    
    def test_schedules_modification_after_init(self):
        """Test behavior when schedules list is modified after initialization."""
        schedules = [[Mock()]]
        controller = generate_controller(schedules)
        
        # Modify the schedules list externally
        schedules.clear()
        
        # Controller should still work with empty schedules
        strings = controller.get_current_schedule_strings()
        self.assertEqual(strings, [])


if __name__ == '__main__':
    unittest.main()