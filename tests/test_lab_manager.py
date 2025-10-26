#!/usr/bin/env python3
"""
Simple Unit Tests for LabManager Class
Tests core functionality: add, modify, delete labs
"""

import unittest
from unittest.mock import patch
from io import StringIO

from src.models.lab_model import LabManager


class TestLabManager(unittest.TestCase):
    """Simple tests for LabManager core functionality"""
    
    def setUp(self):
        """Set up test data for each test"""
        # Simple test data like example.json structure
        self.test_data = {
            "config": {
                "courses": [
                    {
                        "course_id": "CMSC 140",
                        "credits": 4,
                        "lab": ["Linux"],
                        "faculty": ["Hardy"]
                    },
                    {
                        "course_id": "CMSC 161",
                        "credits": 4,
                        "lab": [],  # No labs initially
                        "faculty": ["Zoppetti"]
                    }
                ]
            }
        }
        
        self.lab_manager = LabManager()
        self.lab_manager.data = self.test_data
    
    def test_get_existing_course(self):
        """Test: Should find existing course by ID"""
        course = self.lab_manager.get_course_by_id("CMSC 140")
        
        # Assert: Course should be found with correct data
        self.assertIsNotNone(course, "Should find existing course")
        self.assertEqual(course["course_id"], "CMSC 140", "Should return correct course")
    
    def test_get_nonexistent_course(self):
        """Test: Should return None for non-existent course"""
        course = self.lab_manager.get_course_by_id("CMSC 999")
        
        # Assert: Should return None for course that doesn't exist
        self.assertIsNone(course, "Should return None for non-existent course")
    
    def test_add_lab_success(self):
        """Test: Adding new lab to course should work"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            # Add lab to course that has no labs
            self.lab_manager.add_lab("CMSC 161", "Python")
            
            # Assert: Lab should be added to course
            course = self.lab_manager.get_course_by_id("CMSC 161")
            self.assertIn("Python", course["lab"], "Lab should be added to course")
            
            # Assert: Should print success message
            output = mock_stdout.getvalue()
            self.assertIn("has been added", output, "Should print success message")
    
    def test_add_duplicate_lab(self):
        """Test: Adding duplicate lab should show error"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            # Try to add lab that already exists
            self.lab_manager.add_lab("CMSC 140", "Linux")
            
            # Assert: Should print error message for duplicate
            output = mock_stdout.getvalue()
            self.assertIn("already exists", output, "Should print duplicate error")
    
    def test_modify_lab_success(self):
        """Test: Modifying existing lab should work"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            # Modify existing lab
            self.lab_manager.modify_lab("CMSC 140", "Linux", "Windows")
            
            # Assert: Lab should be changed
            course = self.lab_manager.get_course_by_id("CMSC 140")
            self.assertNotIn("Linux", course["lab"], "Old lab should be removed")
            self.assertIn("Windows", course["lab"], "New lab should be present")
            
            # Assert: Should print success message
            output = mock_stdout.getvalue()
            self.assertIn("has been changed", output, "Should print success message")
    
    def test_modify_nonexistent_lab(self):
        """Test: Modifying lab that doesn't exist should show error"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            # Try to modify lab that doesn't exist
            self.lab_manager.modify_lab("CMSC 140", "Python", "Java")
            
            # Assert: Should print error for lab not found
            output = mock_stdout.getvalue()
            self.assertIn("does not exist in", output, "Should print lab not found error")
    
    def test_delete_lab_success(self):
        """Test: Deleting existing lab should work"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            # Delete existing lab
            self.lab_manager.delete_lab("CMSC 140", "Linux")
            
            # Assert: Lab should be removed
            course = self.lab_manager.get_course_by_id("CMSC 140")
            self.assertNotIn("Linux", course["lab"], "Lab should be deleted")
            
            # Assert: Should print success message
            output = mock_stdout.getvalue()
            self.assertIn("has been deleted", output, "Should print success message")
    
    def test_delete_from_course_no_labs(self):
        """Test: Deleting from course with no labs should show error"""
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            # Try to delete from course with no labs
            self.lab_manager.delete_lab("CMSC 161", "Linux")

            # Assert: Should print no labs error
            output = mock_stdout.getvalue()
            self.assertIn("no lab to delete", output, "Should print no labs error")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)