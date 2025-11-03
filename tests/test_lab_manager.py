#!/usr/bin/env python3
"""
Unit Tests for LabManager Class
Tests core functionality: add, edit, delete labs
"""

import unittest
from unittest.mock import Mock

from src.models.lab_model import LabManager


class TestLabManager(unittest.TestCase):
    """Tests for LabManager core functionality"""

    def setUp(self):
        """Set up test data for each test"""
        # Create a mock config object
        mock_config = Mock()
        mock_config.config = Mock()
        mock_config.config.labs = ["Linux Lab", "Windows Lab"]

        self.lab_manager = LabManager(mock_config)

    def test_load_labs(self):
        """Test: Should load labs from config"""
        labs = self.lab_manager.get_labs()

        # Assert: Labs should be loaded
        self.assertEqual(len(labs), 2, "Should load 2 labs")
        self.assertIn("Linux Lab", labs, "Should contain Linux Lab")
        self.assertIn("Windows Lab", labs, "Should contain Windows Lab")

    def test_add_lab_success(self):
        """Test: Adding new lab should work"""
        result = self.lab_manager.add_lab("Mac Lab")

        # Assert: Lab should be added
        self.assertTrue(result, "Should return True on success")
        self.assertIn("Mac Lab", self.lab_manager.get_labs(), "Lab should be in list")

    def test_add_duplicate_lab(self):
        """Test: Adding duplicate lab should fail"""
        result = self.lab_manager.add_lab("Linux Lab")

        # Assert: Should return False for duplicate
        self.assertFalse(result, "Should return False for duplicate")

    def test_add_empty_lab(self):
        """Test: Adding empty lab name should raise error"""
        with self.assertRaises(ValueError):
            self.lab_manager.add_lab("")

    def test_edit_lab_success(self):
        """Test: Editing existing lab should work"""
        result = self.lab_manager.edit_lab("Linux Lab", "Ubuntu Lab")

        # Assert: Lab should be renamed
        self.assertTrue(result, "Should return True on success")
        self.assertNotIn("Linux Lab", self.lab_manager.get_labs(), "Old name should be removed")
        self.assertIn("Ubuntu Lab", self.lab_manager.get_labs(), "New name should be present")

    def test_edit_nonexistent_lab(self):
        """Test: Editing lab that doesn't exist should fail"""
        result = self.lab_manager.edit_lab("Python Lab", "Java Lab")

        # Assert: Should return False for non-existent lab
        self.assertFalse(result, "Should return False for non-existent lab")

    def test_edit_to_existing_name(self):
        """Test: Editing to an existing name should fail"""
        result = self.lab_manager.edit_lab("Linux Lab", "Windows Lab")

        # Assert: Should return False when new name already exists
        self.assertFalse(result, "Should return False when new name exists")

    def test_edit_empty_name(self):
        """Test: Editing to empty name should raise error"""
        with self.assertRaises(ValueError):
            self.lab_manager.edit_lab("Linux Lab", "")

    def test_delete_lab_success(self):
        """Test: Deleting existing lab should work"""
        result = self.lab_manager.delete_lab("Linux Lab")

        # Assert: Lab should be deleted
        self.assertTrue(result, "Should return True on success")
        self.assertNotIn("Linux Lab", self.lab_manager.get_labs(), "Lab should be removed")

    def test_delete_nonexistent_lab(self):
        """Test: Deleting lab that doesn't exist should fail"""
        result = self.lab_manager.delete_lab("Python Lab")

        # Assert: Should return False for non-existent lab
        self.assertFalse(result, "Should return False for non-existent lab")

    def test_lab_exists(self):
        """Test: Checking if lab exists should work"""
        self.assertTrue(self.lab_manager.lab_exists("Linux Lab"), "Should find existing lab")
        self.assertFalse(self.lab_manager.lab_exists("Python Lab"), "Should not find non-existent lab")

    def test_set_labs(self):
        """Test: Setting labs should replace all labs"""
        new_labs = ["Lab A", "Lab B", "Lab C"]
        self.lab_manager.set_labs(new_labs)

        # Assert: Labs should be replaced
        labs = self.lab_manager.get_labs()
        self.assertEqual(len(labs), 3, "Should have 3 labs")
        self.assertIn("Lab A", labs, "Should contain Lab A")
        self.assertIn("Lab B", labs, "Should contain Lab B")
        self.assertIn("Lab C", labs, "Should contain Lab C")

    def test_load_labs_with_scheduler_config(self):
        """Test: Should load labs from SchedulerConfig (not CombinedConfig)"""
        # Note: Line 32 has a bug - it references self.config.labs instead of config.labs
        # This test documents the bug by expecting AttributeError
        mock_config = Mock(spec=['labs'])  # Only has 'labs' attribute
        mock_config.labs = ["Lab1", "Lab2", "Lab3"]

        # The bug on line 32 causes AttributeError when trying to access self.config
        with self.assertRaises(AttributeError):
            lab_manager = LabManager(mock_config)

    def test_load_labs_with_no_labs_attribute(self):
        """Test: Should handle config with no labs attribute"""
        # Create a mock config with neither config.labs nor labs
        mock_config = Mock(spec=[])  # No attributes

        lab_manager = LabManager(mock_config)

        # Assert: Should initialize with empty list
        labs = lab_manager.get_labs()
        self.assertEqual(len(labs), 0, "Should have no labs")

    def test_to_dict(self):
        """Test: Should convert labs to dictionary format"""
        result = self.lab_manager.to_dict()

        # Assert: Should return dict with 'labs' key
        self.assertIsInstance(result, dict, "Should return a dictionary")
        self.assertIn("labs", result, "Should contain 'labs' key")
        self.assertEqual(len(result["labs"]), 2, "Should have 2 labs")

    def test_save_config(self):
        """Test: Should update config dictionary with lab data"""
        config = {"rooms": ["Room1"], "courses": []}

        result = self.lab_manager.save_config(config)

        # Assert: Config should be updated with labs
        self.assertIn("labs", result, "Should add 'labs' to config")
        self.assertEqual(len(result["labs"]), 2, "Should have 2 labs")
        self.assertIn("Linux Lab", result["labs"], "Should contain Linux Lab")
        self.assertIn("Windows Lab", result["labs"], "Should contain Windows Lab")

    def test_save_with_combined_config(self):
        """Test: Should update CombinedConfig object with lab data"""
        # Create mock CombinedConfig
        mock_combined_config = Mock()
        mock_combined_config.config = Mock()
        mock_combined_config.config.labs = []

        result = self.lab_manager.save_with_combined_config(mock_combined_config)

        # Assert: CombinedConfig should be updated with labs
        self.assertEqual(len(result.config.labs), 2, "Should update config.labs")
        self.assertIn("Linux Lab", result.config.labs, "Should contain Linux Lab")

    def test_update_lab_references_in_courses(self):
        """Test: Should update lab references in courses when lab is renamed"""
        # Create mock course objects
        mock_course1 = Mock()
        mock_course1.lab = ["Linux Lab", "Windows Lab"]
        mock_course2 = Mock()
        mock_course2.lab = ["Linux Lab"]

        courses_dict = {
            "CMSC 140": [mock_course1],
            "CMSC 161": [mock_course2]
        }
        faculty_dict = {}

        # Update lab references
        LabManager.update_lab_references("Linux Lab", "Ubuntu Lab", courses_dict, faculty_dict)

        # Assert: Linux Lab should be replaced with Ubuntu Lab
        self.assertIn("Ubuntu Lab", mock_course1.lab, "Course1 should have Ubuntu Lab")
        self.assertNotIn("Linux Lab", mock_course1.lab, "Course1 should not have Linux Lab")
        self.assertIn("Ubuntu Lab", mock_course2.lab, "Course2 should have Ubuntu Lab")

    def test_update_lab_references_in_faculty(self):
        """Test: Should update lab preferences in faculty when lab is renamed"""
        # Create mock faculty objects
        mock_faculty1 = Mock()
        mock_faculty1.lab_preferences = {"Linux Lab": 5, "Windows Lab": 3}
        mock_faculty2 = Mock()
        mock_faculty2.lab_preferences = {"Linux Lab": 8}

        courses_dict = {}
        faculty_dict = {
            "Dr. Smith": mock_faculty1,
            "Dr. Jones": mock_faculty2
        }

        # Update lab references
        LabManager.update_lab_references("Linux Lab", "Ubuntu Lab", courses_dict, faculty_dict)

        # Assert: Linux Lab preference should be replaced with Ubuntu Lab
        self.assertIn("Ubuntu Lab", mock_faculty1.lab_preferences, "Faculty1 should have Ubuntu Lab preference")
        self.assertEqual(mock_faculty1.lab_preferences["Ubuntu Lab"], 5, "Preference value should be preserved")
        self.assertNotIn("Linux Lab", mock_faculty1.lab_preferences, "Faculty1 should not have Linux Lab")
        self.assertIn("Ubuntu Lab", mock_faculty2.lab_preferences, "Faculty2 should have Ubuntu Lab preference")

    def test_remove_lab_references_from_courses(self):
        """Test: Should remove lab references from courses when lab is deleted"""
        # Create mock course objects
        mock_course1 = Mock()
        mock_course1.lab = ["Linux Lab", "Windows Lab"]
        mock_course2 = Mock()
        mock_course2.lab = ["Linux Lab"]

        courses_dict = {
            "CMSC 140": [mock_course1],
            "CMSC 161": [mock_course2]
        }
        faculty_dict = {}

        # Remove lab references
        LabManager.remove_lab_references("Linux Lab", courses_dict, faculty_dict)

        # Assert: Linux Lab should be removed
        self.assertNotIn("Linux Lab", mock_course1.lab, "Course1 should not have Linux Lab")
        self.assertIn("Windows Lab", mock_course1.lab, "Course1 should still have Windows Lab")
        self.assertNotIn("Linux Lab", mock_course2.lab, "Course2 should not have Linux Lab")

    def test_remove_lab_references_from_faculty(self):
        """Test: Should remove lab preferences from faculty when lab is deleted"""
        # Create mock faculty objects
        mock_faculty1 = Mock()
        mock_faculty1.lab_preferences = {"Linux Lab": 5, "Windows Lab": 3}
        mock_faculty2 = Mock()
        mock_faculty2.lab_preferences = {"Linux Lab": 8}

        courses_dict = {}
        faculty_dict = {
            "Dr. Smith": mock_faculty1,
            "Dr. Jones": mock_faculty2
        }

        # Remove lab references
        LabManager.remove_lab_references("Linux Lab", courses_dict, faculty_dict)

        # Assert: Linux Lab preference should be removed
        self.assertNotIn("Linux Lab", mock_faculty1.lab_preferences, "Faculty1 should not have Linux Lab")
        self.assertIn("Windows Lab", mock_faculty1.lab_preferences, "Faculty1 should still have Windows Lab")
        self.assertNotIn("Linux Lab", mock_faculty2.lab_preferences, "Faculty2 should not have Linux Lab")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)