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


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)