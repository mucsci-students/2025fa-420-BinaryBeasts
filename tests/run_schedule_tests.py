#!/usr/bin/env python3
"""
Test runner for schedule visualization components.
Run this script to execute all schedule visualization tests.
"""


"""""
### Run All Schedule Visualization Tests
```bash
# From project root
python -m unittest tests.test_room_day_model tests.test_schedules_controller tests.test_schedule_visualization_view tests.test_schedule_visualization_integration -v

### Run Individual Test Files
```bash
# Test room/day model only
python -m unittest tests.test_room_day_model -v

# Test schedules controller only  
python -m unittest tests.test_schedules_controller -v

# Test visualization view only
python -m unittest tests.test_schedule_visualization_view -v

# Test integration only
python -m unittest tests.test_schedule_visualization_integration -v
"""

import unittest
import sys
import os

def run_schedule_visualization_tests():
    """Run all schedule visualization tests."""
    
    # Import test modules directly
    try:
        import test_room_day_model
        import test_schedules_controller
        import test_schedule_visualization_view
        import test_schedule_visualization_integration
    except ImportError as e:
        print(f"Error importing test modules: {e}")
        print("Make sure you're running this from the tests directory or the project root.")
        return False
    
    print("=" * 70)
    print("RUNNING SCHEDULE VISUALIZATION TESTS")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests from each module
    suite.addTests(loader.loadTestsFromModule(test_room_day_model))
    suite.addTests(loader.loadTestsFromModule(test_schedules_controller))
    suite.addTests(loader.loadTestsFromModule(test_schedule_visualization_view))
    suite.addTests(loader.loadTestsFromModule(test_schedule_visualization_integration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%" if result.testsRun > 0 else "N/A")
    
    if result.failures:
        print(f"\nFAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    return result.wasSuccessful()


def run_individual_test_module(module_name):
    """Run tests for a specific module."""
    
    valid_modules = {
        'room_day': 'tests.test_room_day_model',
        'controller': 'tests.test_schedules_controller', 
        'view': 'tests.test_schedule_visualization_view',
        'integration': 'tests.test_schedule_visualization_integration'
    }
    
    if module_name not in valid_modules:
        print(f"Invalid module name. Choose from: {list(valid_modules.keys())}")
        return False
    
    test_module = valid_modules[module_name]
    
    print(f"Running tests for {test_module}...")
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_module)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run specific test module
        module_arg = sys.argv[1].lower()
        success = run_individual_test_module(module_arg)
    else:
        # Run all tests
        success = run_schedule_visualization_tests()
    
    sys.exit(0 if success else 1)