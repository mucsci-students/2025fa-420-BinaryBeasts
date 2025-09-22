#!/usr/bin/env python3
"""
Test file for main.py
Tests JSON loading, input validation, and main workflow functionality.
"""

import unittest
import json
import tempfile
import os
from unittest.mock import patch, mock_open
from io import StringIO
import sys

# Import the modules to test
import main


class TestJSONLoading(unittest.TestCase):
    """Test JSON loading functions."""
    
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
                        "faculty": []
                    }
                ],
            },
            "time_slot_config": {
                "times": {
                    "MON": [{"start": "08:00", "spacing": 60, "end": "17:00"}]
                }
            }
        }
        
        self.config_only = {
            "rooms": ["Roddy 136"],
            "courses": [{"course_id": "CMSC 140", "credits": 4}]
        }
        
        self.time_slots_only = {
            "times": {
                "MON": [{"start": "08:00", "spacing": 60, "end": "17:00"}]
            }
        }
    
    def test_load_config_with_config_section(self):
        """Test loading config when 'config' section exists."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.config_only, f)
            temp_file = f.name
        
        try:
            result = main.load_config(temp_file)
            self.assertEqual(result, self.config_only)
        finally:
            os.unlink(temp_file)
    
    def test_load_time_slot_config_with_section(self):
        """Test loading time slot config when 'time_slot_config' section exists."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_config, f)
            temp_file = f.name
        
        try:
            result = main.load_time_slot_config(temp_file)
            self.assertEqual(result, self.sample_config["time_slot_config"])
            self.assertIn("times", result)
        finally:
            os.unlink(temp_file)
    
    def test_load_time_slot_config_without_section(self):
        """Test loading time slot config when section doesn't exist."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.time_slots_only, f)
            temp_file = f.name
        
        try:
            result = main.load_time_slot_config(temp_file)
            self.assertEqual(result, self.time_slots_only)
        finally:
            os.unlink(temp_file)
    
    def test_load_config_invalid_json(self):
        """Test loading config with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"invalid": json content}')
            temp_file = f.name
        
        try:
            with self.assertRaises(ValueError):
                main.load_config(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_load_config_file_not_found(self):
        """Test loading config with non-existent file."""
        with self.assertRaises(FileNotFoundError):
            main.load_config("nonexistent_file.json")


class TestUserInput(unittest.TestCase):
    """Test user input validation and processing."""
    
    @patch('builtins.input')
    def test_get_user_input_with_defaults(self, mock_input):
        """Test user input with default values."""
        # Mock user inputs: config file, use same file (default), output file, default limit, no optimization
        mock_input.side_effect = ['example.json', '', 'output.json', '', 'n']
        
        result = main.get_user_input()
        
        expected = {
            'config': 'example.json',
            'time_slots': 'example.json',  # Same file
            'output': 'output.json',
            'limit': 10,  # Default
            'optimize': False
        }
        
        self.assertEqual(result, expected)
    
    @patch('builtins.input')
    def test_get_user_input_separate_files(self, mock_input):
        """Test user input with separate config files."""
        mock_input.side_effect = ['config.json', 'no', 'timeslots.json', 'output.json', '25', 'yes']
        
        result = main.get_user_input()
        
        expected = {
            'config': 'config.json',
            'time_slots': 'timeslots.json',
            'output': 'output.json',
            'limit': 25,
            'optimize': True
        }
        
        self.assertEqual(result, expected)
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_get_user_input_invalid_limit_then_valid(self, mock_print, mock_input):
        """Test limit validation with invalid input followed by valid input."""
        # Invalid inputs: 'abc', '0', '1001', then valid '50'
        mock_input.side_effect = [
            'config.json', 'y', 'output.json', 
            'abc', '0', '1001', '50',  # Invalid limits then valid
            'n'
        ]
        
        result = main.get_user_input()
        
        self.assertEqual(result['limit'], 50)
        # Check that error messages were printed
        mock_print.assert_any_call("Error: Please enter a valid number.")
        mock_print.assert_any_call("Error: Please enter a number greater than 0.")
        mock_print.assert_any_call("Error: Please enter a number less than 1000.")
    
    @patch('builtins.input')
    def test_get_user_input_optimization_variants(self, mock_input):
        """Test different optimization input variants."""
        test_cases = [
            ('y', True),
            ('yes', True),
            ('true', True),
            ('1', True),
            ('n', False),
            ('no', False),
            ('false', False),
            ('0', False),
            ('', False),  # Default
            ('random', False)  # Invalid input defaults to False
        ]
        
        for opt_input, expected_optimize in test_cases:
            with self.subTest(opt_input=opt_input):
                mock_input.side_effect = ['config.json', 'y', 'output.json', '10', opt_input]
                result = main.get_user_input()
                self.assertEqual(result['optimize'], expected_optimize)


class TestValidateFilePath(unittest.TestCase):
    """Test file path validation (placeholder since function is not implemented)."""
    
    def test_validate_file_path_placeholder(self):
        """Test that validate_file_path function exists."""
        # Since the function currently just has 'pass', we just test it exists
        self.assertTrue(hasattr(main, 'validate_file_path'))


class TestMainWorkflow(unittest.TestCase):
    """Test the main workflow integration."""
    
    def setUp(self):
        """Set up test files."""
        self.test_config = {
            "config": {
                "rooms": ["Roddy 136", "Roddy 140"],
                "labs": ["Linux", "Mac"],
                "courses": [
                    {
                        "course_id": "CMSC 140",
                        "credits": 4,
                        "room": ["Roddy 136", "Roddy 140"],
                        "lab": [],
                        "conflicts": ["CMSC 161"],
                        "faculty": ["Hardy"]
                    },
                    {
                        "course_id": "CMSC 161",
                        "credits": 4,
                        "room": ["Roddy 136"],
                        "lab": ["Linux"],
                        "conflicts": ["CMSC 140"],
                        "faculty": ["Zoppetti"]
                    }
                ],
                "faculty": [
                    {
                        "name": "Hardy",
                        "maximum_credits": 12,
                        "minimum_credits": 8
                    }
                ]
            },
            "time_slot_config": {
                "times": {
                    "MON": [{"start": "08:00", "spacing": 60, "end": "17:00"}],
                    "TUE": [{"start": "08:00", "spacing": 60, "end": "17:00"}]
                },
                "classes": [
                    {
                        "credits": 4,
                        "meetings": [
                            {"day": "MON", "duration": 110},
                            {"day": "TUE", "duration": 110}
                        ]
                    }
                ]
            }
        }
    
    @patch('builtins.input')
    @patch('main.validate_file_path')
    @patch('main.generate_schedules')
    @patch('main.save_schedules')
    @patch('builtins.print')
    def test_main_successful_execution(self, mock_print, mock_save, mock_generate, 
                                     mock_validate, mock_input):
        """Test successful main execution."""
        # Create temp config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.test_config, f)
            config_file = f.name
        
        try:
            # Mock user input
            mock_input.side_effect = [config_file, 'y', 'output.json', '5', 'n']
            
            # Mock file validation to return Path objects
            from pathlib import Path
            mock_validate.side_effect = [Path(config_file), Path(config_file), Path('output.json')]
            
            # Mock schedule generation
            mock_generate.return_value = [{'schedule': 'test_schedule'}]
            
            # Run main
            main.main()
            
            # Verify calls
            self.assertEqual(mock_validate.call_count, 3)
            mock_generate.assert_called_once()
            mock_save.assert_called_once()
            
            # Check that success message was printed
            mock_print.assert_any_call("Schedule generation completed successfully!")
            
        finally:
            os.unlink(config_file)
    
    @patch('builtins.input')
    @patch('main.load_config')
    @patch('sys.exit')
    @patch('builtins.print')
    def test_main_file_not_found_error(self, mock_print, mock_exit, mock_load, mock_input):
        """Test main function handling FileNotFoundError."""
        mock_input.side_effect = ['nonexistent.json', 'y', 'output.json', '10', 'n']
        mock_load.side_effect = FileNotFoundError("Config file not found")
        
        main.main()
        
        mock_exit.assert_called_with(1)
        # Check error message was printed to stderr
        self.assertTrue(any('File not found' in str(call) for call in mock_print.call_args_list))
    
    @patch('builtins.input')
    @patch('main.load_config')
    @patch('sys.exit')
    @patch('builtins.print')
    def test_main_json_decode_error(self, mock_print, mock_exit, mock_load, mock_input):
        """Test main function handling JSON decode error."""
        mock_input.side_effect = ['invalid.json', 'y', 'output.json', '10', 'n']
        mock_load.side_effect = ValueError("Invalid JSON")
        
        main.main()
        
        mock_exit.assert_called_with(1)
        # Check error message was printed
        self.assertTrue(any('Invalid input' in str(call) for call in mock_print.call_args_list))


class TestIntegrationWithExampleJSON(unittest.TestCase):
    """Integration tests using the actual example.json file."""
    
    def test_load_actual_example_json(self):
        """Test loading the actual example.json file if it exists."""
        example_file = "../example.json"
        if os.path.exists(example_file):
            try:
                config = main.load_config(example_file)
                time_slots = main.load_time_slot_config(example_file)
                
                # Verify expected structure
                self.assertIn("rooms", config)
                self.assertIn("courses", config)
                self.assertIn("faculty", config)
                self.assertIn("times", time_slots)
                self.assertIn("classes", time_slots)
                
                # Verify course structure
                courses = config["courses"]
                self.assertGreater(len(courses), 0)
                
                first_course = courses[0]
                self.assertIn("course_id", first_course)
                self.assertIn("credits", first_course)
                self.assertIn("room", first_course)
                self.assertIn("lab", first_course)
                self.assertIn("conflicts", first_course)
                self.assertIn("faculty", first_course)
                
            except Exception as e:
                self.fail(f"Failed to load example.json: {e}")
        else:
            self.skipTest("example.json not found in current directory")


def run_interactive_test():
    """
    Run an interactive test of the main program.
    This function simulates user interaction for manual testing.
    """
    print("=== Interactive Test of main.py ===")
    print("This will run the actual main() function.")
    print("You can test with 'example.json' if it exists in the current directory.")
    print("Press Ctrl+C to cancel.\n")
    
    try:
        main.main()
    except KeyboardInterrupt:
        print("\nTest cancelled by user.")
    except Exception as e:
        print(f"Error during interactive test: {e}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test main.py functionality')
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run interactive test instead of unit tests')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output for unit tests')
    
    args = parser.parse_args()
    
    if args.interactive:
        run_interactive_test()
    else:
        # Run unit tests
        verbosity = 2 if args.verbose else 1
        unittest.main(argv=[''], verbosity=verbosity, exit=False)
        
        print("\n" + "="*50)
        print("Test Summary:")
        print("- JSON loading functions tested")
        print("- User input validation tested") 
        print("- Error handling tested")
        print("- Integration scenarios tested")
        print("\nTo run interactive test: python test_main.py --interactive")
        print("To run with verbose output: python test_main.py --verbose")