#!/usr/bin/env python3
"""
Updated test file for main.py
Tests the current scheduler integration functionality.
"""

import unittest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
import sys

# Add the src directory to the path to import main this works for some reason importing main
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import main


class TestJSONLoading(unittest.TestCase):
    """Test JSON loading functions that still exist."""

    def setUp(self):
        """Set up test data."""
        self.sample_config = {
            "config": {
                "rooms": ["Roddy 136", "Roddy 140"],
                "labs": ["Linux", "Mac"],
                "courses": [
                    {
                        "course_id": "CMSC 140",
                        "credits": 4,
                        "room": ["Roddy 136"],
                        "lab": [],
                        "conflicts": ["CMSC 161"],
                        "faculty": [],
                    }
                ],
            },
            "time_slot_config": {
                "times": {"MON": [{"start": "08:00", "spacing": 60, "end": "17:00"}]}
            },
        }

        self.config_only = {
            "rooms": ["Roddy 136"],
            "courses": [{"course_id": "CMSC 140", "credits": 4}],
        }

    def test_load_config_with_config_section(self):
        """Test loading config when 'config' section exists."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(self.sample_config, f)
            temp_file = f.name

        try:
            result = main.load_config(temp_file)
            self.assertEqual(result, self.sample_config["config"])
            self.assertIn("rooms", result)
            self.assertIn("courses", result)
        finally:
            os.unlink(temp_file)

    def test_load_config_without_config_section(self):
        """Test loading config when 'config' section doesn't exist."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(self.config_only, f)
            temp_file = f.name

        try:
            result = main.load_config(temp_file)
            self.assertEqual(result, self.config_only)
        finally:
            os.unlink(temp_file)

    def test_load_time_slot_config_with_section(self):
        """Test loading time slot config when 'time_slot_config' section exists."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(self.sample_config, f)
            temp_file = f.name

        try:
            result = main.load_time_slot_config(temp_file)
            self.assertEqual(result, self.sample_config["time_slot_config"])
            self.assertIn("times", result)
        finally:
            os.unlink(temp_file)


class TestInterfaceSelection(unittest.TestCase):
    """Test interface selection functionality."""

    @patch("builtins.input")
    def test_show_interface_selection_cli(self, mock_input):
        """Test interface selection returns CLI choice."""
        mock_input.return_value = "1"
        result = main.show_interface_selection()
        self.assertEqual(result, "1")

    @patch("builtins.input")
    def test_show_interface_selection_gui(self, mock_input):
        """Test interface selection returns GUI choice."""
        mock_input.return_value = "2"
        result = main.show_interface_selection()
        self.assertEqual(result, "2")

    @patch("builtins.input")
    def test_show_main_menu(self, mock_input):
        """Test main menu returns user choice."""
        mock_input.return_value = "5"  # Generate Schedules
        result = main.show_main_menu()
        self.assertEqual(result, "5")


class TestScheduleGeneration(unittest.TestCase):
    """Test schedule generation functionality."""

    @patch("builtins.input")
    @patch("main.load_config_from_file")
    @patch("main.Scheduler")
    @patch("main.save_schedules_to_file")
    @patch("builtins.print")
    def test_generate_schedules_interactive_success(
        self, mock_print, mock_save, mock_scheduler_class, mock_load, mock_input
    ):
        """Test successful schedule generation."""
        # Mock user inputs: no preview, default limit, json format, default filename, confirm, final enter
        mock_input.side_effect = ["n", "", "json", "", "y", ""]

        # Mock scheduler
        mock_config = MagicMock()
        mock_load.return_value = mock_config

        mock_scheduler = MagicMock()
        mock_scheduler_class.return_value = mock_scheduler

        # Mock schedule generation
        mock_course = MagicMock()
        mock_course.as_csv.return_value = (
            "CMSC140,MON,09:00,110,Roddy136,Linux,Dr.Smith"
        )
        mock_schedule = [mock_course]
        mock_scheduler.get_models.return_value = [mock_schedule]

        # Test data
        config_file = "test.json"
        full_config = {"config": {"courses": []}}
        time_slots = {"times": {}}

        # Run function
        main.generate_schedules_interactive(config_file, full_config, time_slots)

        # Verify calls
        mock_load.assert_called_once()
        mock_scheduler_class.assert_called_once()
        mock_save.assert_called_once()

    @patch("builtins.input")
    @patch("main.load_config_from_file")
    @patch("main.Scheduler")
    @patch("builtins.print")
    def test_generate_schedules_interactive_no_schedules(
        self, mock_print, mock_scheduler_class, mock_load, mock_input
    ):
        """Test schedule generation when no schedules can be generated."""
        # Mock user inputs
        mock_input.side_effect = ["n", "", "json", "", "y"]

        # Mock scheduler that returns no schedules
        mock_config = MagicMock()
        mock_load.return_value = mock_config

        mock_scheduler = MagicMock()
        mock_scheduler_class.return_value = mock_scheduler
        mock_scheduler.get_models.return_value = []  # No schedules generated

        # Test data
        config_file = "test.json"
        full_config = {"config": {"courses": []}}
        time_slots = {"times": {}}

        # Run function
        main.generate_schedules_interactive(config_file, full_config, time_slots)

        # Verify error message was printed
        mock_print.assert_any_call("❌ No valid schedules could be generated.")

    @patch("builtins.input")
    def test_generate_schedules_interactive_cancelled(self, mock_input):
        """Test schedule generation when user cancels."""
        # Mock user inputs: no preview, default settings, but don't confirm
        mock_input.side_effect = ["n", "", "json", "", "n"]

        # Test data
        config_file = "test.json"
        full_config = {"config": {"courses": []}}
        time_slots = {"times": {}}

        # Run function - should return without generating
        with patch("builtins.print") as mock_print:
            main.generate_schedules_interactive(config_file, full_config, time_slots)
            mock_print.assert_any_call("Schedule generation cancelled.")


class TestFilePath(unittest.TestCase):
    """Test file path validation."""

    def test_validate_file_path_exists(self):
        """Test that validate_file_path function exists."""
        self.assertTrue(hasattr(main, "validate_file_path"))

        # Create a temporary file to test with
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_file = f.name

        try:
            # Test that function can be called (even if it just returns the path)
            result = main.validate_file_path(temp_file, must_exist=True)
            self.assertIsNotNone(result)
        finally:
            os.unlink(temp_file)


class TestSaveSchedules(unittest.TestCase):
    """Test schedule saving functionality."""

    def test_save_schedules_to_file_csv(self):
        """Test saving schedules to CSV format."""
        # Mock schedule data
        mock_course = MagicMock()
        mock_course.as_csv.return_value = (
            "CMSC140,MON,09:00,110,Roddy136,Linux,Dr.Smith"
        )
        mock_schedule = [mock_course]
        schedules = [mock_schedule]

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_file = f.name

        try:
            # Test CSV saving
            main.save_schedules_to_file(schedules, temp_file, "csv")

            # Verify file was created and has content
            self.assertTrue(os.path.exists(temp_file))
            with open(temp_file, "r") as f:
                content = f.read()
                self.assertIn(
                    "Schedule,Course,Day,Time,Duration,Room,Lab,Faculty", content
                )
                self.assertIn("CMSC140", content)
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_save_schedules_to_file_json(self):
        """Test saving schedules to JSON format."""
        # Mock schedule data
        mock_course = MagicMock()
        mock_course.as_csv.return_value = (
            "CMSC140,MON,09:00,110,Roddy136,Linux,Dr.Smith"
        )
        mock_schedule = [mock_course]
        schedules = [mock_schedule]

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_file = f.name

        try:
            # Test JSON saving
            main.save_schedules_to_file(schedules, temp_file, "json")

            # Verify file was created and has valid JSON
            self.assertTrue(os.path.exists(temp_file))
            with open(temp_file, "r") as f:
                data = json.load(f)
                self.assertIsInstance(data, list)
                self.assertEqual(len(data), 1)
                self.assertIn("schedule_id", data[0])
                self.assertIn("courses", data[0])
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestPrintConfigSummary(unittest.TestCase):
    """Test configuration summary printing."""

    @patch("builtins.print")
    def test_print_config_summary(self, mock_print):
        """Test that config summary prints correctly."""
        config = {
            "rooms": ["Roddy 136"],
            "labs": ["Linux"],
            "courses": [{"course_id": "CMSC 140", "credits": 4}],
            "faculty": [{"name": "Dr. Smith"}],
        }
        time_slots = {
            "times": {"MON": [{"start": "08:00", "end": "17:00"}]},
            "classes": [{"credits": 4}],
        }

        main.print_config_summary(config, time_slots)

        # Verify summary sections were printed
        mock_print.assert_any_call("CONFIGURATION SUMMARY")
        # Check that some key information was printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        summary_text = " ".join(print_calls)
        self.assertIn("ROOMS", summary_text)
        self.assertIn("COURSES", summary_text)
        self.assertIn("FACULTY", summary_text)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test updated main.py functionality")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output for unit tests"
    )

    args = parser.parse_args()

    # Run unit tests
    verbosity = 2 if args.verbose else 1
    unittest.main(argv=[""], verbosity=verbosity, exit=False)

    print("\n" + "=" * 50)
    print("Updated Test Summary:")
    print("- JSON loading functions tested")
    print("- Interface selection tested")
    print("- Schedule generation tested")
    print("- File operations tested")
    print("- Configuration summary tested")
