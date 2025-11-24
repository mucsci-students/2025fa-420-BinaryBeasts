"""
Tests for the TimeSlotManager class.

Comprehensive test suite covering all functionality of the TimeSlotManager
including CRUD operations, configuration validation, observer pattern
integration, and error handling.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from pydantic import ValidationError

from src.models.time_slot_model import TimeSlotManager
from src.observer_pattern import Observer, EventType, EventData


class MockObserver(Observer):
    """Mock observer for testing observer pattern functionality."""
    
    def __init__(self):
        self.notifications = []
    
    def update(self, event_type: EventType, data: EventData = None) -> None:
        """Record notifications for testing."""
        self.notifications.append({
            'event_type': event_type,
            'data': data.extra_data if data else None
        })
    
    def clear(self):
        """Clear recorded notifications."""
        self.notifications.clear()


class TestTimeSlotManagerInitialization:
    """Test initialization and basic setup of TimeSlotManager."""
    
    def test_initialization_empty(self):
        """Test creating TimeSlotManager with no configuration."""
        manager = TimeSlotManager()
        assert manager.time_slot_config is None
        assert manager._original_config is None
        assert manager._observers == []
    
    def test_initialization_with_config(self):
        """Test creating TimeSlotManager with initial configuration."""
        config = {"times": {}, "classes": []}
        manager = TimeSlotManager(time_slot_config=config)
        assert manager.time_slot_config == config
        assert manager._original_config is None


class TestTimeSlotManagerConfiguration:
    """Test configuration loading and management."""
    
    def test_load_valid_configuration(self):
        """Test loading a valid time slot configuration."""
        manager = TimeSlotManager()
        observer = MockObserver()
        manager.add_observer(observer)
        
        config = {
            "times": {
                "MON": [{"start": "08:00", "end": "09:50", "spacing": 60}],
                "TUE": [{"start": "10:00", "end": "11:50", "spacing": 60}]
            },
            "classes": [
                {
                    "credits": 3,
                    "meetings": [{"day": "MON", "duration": 110}]
                }
            ],
            "max_time_gap": 180,
            "min_time_overlap": 30
        }
        
        manager.load_time_slots(config)
        
        assert manager.time_slot_config == config
        assert manager._original_config == config
        
        # Check observer notification
        assert len(observer.notifications) == 1
        assert observer.notifications[0]['event_type'] == EventType.COURSES_LOADED
        assert observer.notifications[0]['data']['data']['time_slot_config'] == config
    
    def test_load_invalid_configuration_type(self):
        """Test loading invalid configuration type raises error."""
        manager = TimeSlotManager()
        
        with pytest.raises(ValueError, match="Time slot data must be a dictionary"):
            manager.load_time_slots("invalid")
    
    def test_load_configuration_with_exception(self):
        """Test error handling during configuration loading."""
        manager = TimeSlotManager()
        
        # Create a config that will cause an exception during processing
        with patch.object(manager, 'notify_observers', side_effect=Exception("Test error")):
            with pytest.raises(ValueError, match="Failed to load time slot configuration"):
                manager.load_time_slots({"times": {}, "classes": []})
    
    def test_get_time_slot_config(self):
        """Test retrieving the current configuration."""
        config = {"times": {}, "classes": []}
        manager = TimeSlotManager(time_slot_config=config)
        
        assert manager.get_time_slot_config() == config
    
    def test_get_time_slot_config_none(self):
        """Test retrieving configuration when none is loaded."""
        manager = TimeSlotManager()
        assert manager.get_time_slot_config() is None


class TestTimeSlotManagerTimeBlocks:
    """Test time block management functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            "times": {
                "MON": [{"start": "08:00", "end": "09:50", "spacing": 60}],
                "TUE": []
            },
            "classes": []
        }
        self.manager = TimeSlotManager(time_slot_config=self.config)
        self.observer = MockObserver()
        self.manager.add_observer(self.observer)
    
    def test_get_time_blocks_for_day_existing(self):
        """Test getting time blocks for an existing day."""
        blocks = self.manager.get_time_blocks_for_day("MON")
        expected = [{"start": "08:00", "end": "09:50", "spacing": 60}]
        assert blocks == expected
    
    def test_get_time_blocks_for_day_empty(self):
        """Test getting time blocks for a day with no blocks."""
        blocks = self.manager.get_time_blocks_for_day("TUE")
        assert blocks == []
    
    def test_get_time_blocks_for_day_nonexistent(self):
        """Test getting time blocks for a non-existent day."""
        blocks = self.manager.get_time_blocks_for_day("WED")
        assert blocks == []
    
    def test_get_time_blocks_no_config(self):
        """Test getting time blocks when no configuration is loaded."""
        manager = TimeSlotManager()
        blocks = manager.get_time_blocks_for_day("MON")
        assert blocks == []
    
    def test_get_all_days(self):
        """Test getting all configured days."""
        days = self.manager.get_all_days()
        assert set(days) == {"MON", "TUE"}
    
    def test_get_all_days_no_config(self):
        """Test getting all days when no configuration is loaded."""
        manager = TimeSlotManager()
        days = manager.get_all_days()
        assert days == []
    
    def test_add_time_block_success(self):
        """Test successfully adding a time block."""
        new_block = {"start": "14:00", "end": "15:50"}
        
        result = self.manager.add_time_block("TUE", new_block)
        
        assert result is True
        blocks = self.manager.get_time_blocks_for_day("TUE")
        assert len(blocks) == 1
        # Check that spacing was added automatically
        assert blocks[0]["spacing"] == 60
        
        # Check observer notification
        assert len(self.observer.notifications) == 1
        assert self.observer.notifications[0]['event_type'] == EventType.COURSE_ADDED
    
    def test_add_time_block_new_day(self):
        """Test adding a time block to a new day."""
        new_block = {"start": "10:00", "end": "11:50"}
        
        result = self.manager.add_time_block("WED", new_block)
        
        assert result is True
        assert "WED" in self.manager.time_slot_config["times"]
        blocks = self.manager.get_time_blocks_for_day("WED")
        assert len(blocks) == 1
    
    def test_add_time_block_missing_required_field(self):
        """Test adding time block with missing required fields."""
        incomplete_block = {"start": "10:00"}  # Missing 'end'
        
        result = self.manager.add_time_block("TUE", incomplete_block)
        
        assert result is False
    
    def test_add_time_block_no_config(self):
        """Test adding time block when no configuration is loaded."""
        manager = TimeSlotManager()
        result = manager.add_time_block("MON", {"start": "10:00", "end": "11:50"})
        assert result is False
    
    def test_remove_time_block_success(self):
        """Test successfully removing a time block."""
        result = self.manager.remove_time_block("MON", 0)
        
        assert result is True
        blocks = self.manager.get_time_blocks_for_day("MON")
        assert len(blocks) == 0
        
        # Check observer notification
        assert len(self.observer.notifications) == 1
        assert self.observer.notifications[0]['event_type'] == EventType.COURSE_REMOVED
    
    def test_remove_time_block_invalid_index(self):
        """Test removing time block with invalid index."""
        result = self.manager.remove_time_block("MON", 5)
        assert result is False
    
    def test_remove_time_block_nonexistent_day(self):
        """Test removing time block from non-existent day."""
        result = self.manager.remove_time_block("WED", 0)
        assert result is False
    
    def test_remove_time_block_no_config(self):
        """Test removing time block when no configuration is loaded."""
        manager = TimeSlotManager()
        result = manager.remove_time_block("MON", 0)
        assert result is False
    
    def test_modify_time_block_success(self):
        """Test successfully modifying a time block."""
        new_block = {"start": "09:00", "end": "10:50", "spacing": 90}
        
        result = self.manager.modify_time_block("MON", 0, new_block)
        
        assert result is True
        blocks = self.manager.get_time_blocks_for_day("MON")
        assert blocks[0] == new_block
        
        # Check observer notification
        assert len(self.observer.notifications) == 1
        assert self.observer.notifications[0]['event_type'] == EventType.COURSE_UPDATED
    
    def test_modify_time_block_preserve_spacing(self):
        """Test modifying time block preserves spacing when not provided."""
        original_spacing = self.manager.time_slot_config["times"]["MON"][0]["spacing"]
        new_block = {"start": "09:00", "end": "10:50"}
        
        result = self.manager.modify_time_block("MON", 0, new_block)
        
        assert result is True
        blocks = self.manager.get_time_blocks_for_day("MON")
        assert blocks[0]["spacing"] == original_spacing
    
    def test_modify_time_block_invalid_index(self):
        """Test modifying time block with invalid index."""
        result = self.manager.modify_time_block("MON", 5, {"start": "09:00", "end": "10:50"})
        assert result is False
    
    def test_modify_time_block_exception(self):
        """Test modifying time block handles exceptions gracefully."""
        with patch.object(self.manager, 'notify_observers', side_effect=Exception("Test error")):
            result = self.manager.modify_time_block("MON", 0, {"start": "09:00", "end": "10:50"})
            assert result is False


class TestTimeSlotManagerClassPatterns:
    """Test class pattern management functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            "times": {},
            "classes": [
                {
                    "credits": 3,
                    "meetings": [{"day": "MON", "duration": 110}],
                    "disabled": False
                }
            ]
        }
        self.manager = TimeSlotManager(time_slot_config=self.config)
        self.observer = MockObserver()
        self.manager.add_observer(self.observer)
    
    def test_get_class_patterns(self):
        """Test getting all class patterns."""
        patterns = self.manager.get_class_patterns()
        assert len(patterns) == 1
        assert patterns[0]["credits"] == 3
    
    def test_get_class_patterns_no_config(self):
        """Test getting class patterns when no configuration is loaded."""
        manager = TimeSlotManager()
        patterns = manager.get_class_patterns()
        assert patterns == []
    
    def test_get_enabled_class_patterns(self):
        """Test getting only enabled class patterns."""
        # Add a disabled pattern
        disabled_pattern = {
            "credits": 4,
            "meetings": [{"day": "TUE", "duration": 150}],
            "disabled": True
        }
        self.manager.time_slot_config["classes"].append(disabled_pattern)
        
        enabled = self.manager.get_enabled_class_patterns()
        assert len(enabled) == 1
        assert enabled[0]["credits"] == 3
    
    def test_add_class_pattern_success(self):
        """Test successfully adding a class pattern."""
        new_pattern = {
            "credits": 4,
            "meetings": [
                {"day": "TUE", "duration": 110},
                {"day": "THU", "duration": 110}
            ]
        }
        
        result = self.manager.add_class_pattern(new_pattern)
        
        assert result is True
        patterns = self.manager.get_class_patterns()
        assert len(patterns) == 2
        
        # Check observer notification
        assert len(self.observer.notifications) == 1
        assert self.observer.notifications[0]['event_type'] == EventType.LAB_ADDED
    
    def test_add_class_pattern_missing_credits(self):
        """Test adding class pattern with missing credits field."""
        invalid_pattern = {
            "meetings": [{"day": "TUE", "duration": 110}]
        }
        
        result = self.manager.add_class_pattern(invalid_pattern)
        assert result is False
    
    def test_add_class_pattern_missing_meetings(self):
        """Test adding class pattern with missing meetings field."""
        invalid_pattern = {"credits": 3}
        
        result = self.manager.add_class_pattern(invalid_pattern)
        assert result is False
    
    def test_add_class_pattern_empty_meetings(self):
        """Test adding class pattern with empty meetings."""
        invalid_pattern = {
            "credits": 3,
            "meetings": []
        }
        
        result = self.manager.add_class_pattern(invalid_pattern)
        assert result is False
    
    def test_add_class_pattern_invalid_meeting(self):
        """Test adding class pattern with invalid meeting structure."""
        invalid_pattern = {
            "credits": 3,
            "meetings": [{"day": "MON"}]  # Missing duration
        }
        
        result = self.manager.add_class_pattern(invalid_pattern)
        assert result is False
    
    def test_add_class_pattern_no_config(self):
        """Test adding class pattern when no configuration is loaded."""
        manager = TimeSlotManager()
        result = manager.add_class_pattern({"credits": 3, "meetings": [{"day": "MON", "duration": 110}]})
        assert result is False
    
    def test_remove_class_pattern_success(self):
        """Test successfully removing a class pattern."""
        result = self.manager.remove_class_pattern(0)
        
        assert result is True
        patterns = self.manager.get_class_patterns()
        assert len(patterns) == 0
        
        # Check observer notification
        assert len(self.observer.notifications) == 1
        assert self.observer.notifications[0]['event_type'] == EventType.LAB_REMOVED
    
    def test_remove_class_pattern_invalid_index(self):
        """Test removing class pattern with invalid index."""
        result = self.manager.remove_class_pattern(5)
        assert result is False
    
    def test_remove_class_pattern_no_config(self):
        """Test removing class pattern when no configuration is loaded."""
        manager = TimeSlotManager()
        result = manager.remove_class_pattern(0)
        assert result is False
    
    def test_modify_class_pattern_success(self):
        """Test successfully modifying a class pattern."""
        new_pattern = {
            "credits": 4,
            "meetings": [{"day": "WED", "duration": 150}]
        }
        
        result = self.manager.modify_class_pattern(0, new_pattern)
        
        assert result is True
        patterns = self.manager.get_class_patterns()
        assert patterns[0] == new_pattern
        
        # Check observer notification
        assert len(self.observer.notifications) == 1
        assert self.observer.notifications[0]['event_type'] == EventType.LAB_UPDATED
    
    def test_modify_class_pattern_invalid_index(self):
        """Test modifying class pattern with invalid index."""
        result = self.manager.modify_class_pattern(5, {"credits": 4, "meetings": []})
        assert result is False
    
    def test_toggle_pattern_status_enable_to_disable(self):
        """Test toggling pattern status from enabled to disabled."""
        result = self.manager.toggle_pattern_status(0)
        
        assert result is True
        patterns = self.manager.get_class_patterns()
        assert patterns[0]["disabled"] is True
        
        # Check observer notification
        assert len(self.observer.notifications) == 1
        assert self.observer.notifications[0]['event_type'] == EventType.FACULTY_UPDATED
    
    def test_toggle_pattern_status_disable_to_enable(self):
        """Test toggling pattern status from disabled to enabled."""
        # First disable the pattern
        self.manager.time_slot_config["classes"][0]["disabled"] = True
        
        result = self.manager.toggle_pattern_status(0)
        
        assert result is True
        patterns = self.manager.get_class_patterns()
        assert patterns[0]["disabled"] is False
    
    def test_toggle_pattern_status_invalid_index(self):
        """Test toggling pattern status with invalid index."""
        result = self.manager.toggle_pattern_status(5)
        assert result is False


class TestTimeSlotManagerGapSettings:
    """Test gap settings management functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            "times": {},
            "classes": [],
            "max_time_gap": 180,
            "min_time_overlap": 30
        }
        self.manager = TimeSlotManager(time_slot_config=self.config)
        self.observer = MockObserver()
        self.manager.add_observer(self.observer)
    
    def test_update_gap_settings_both(self):
        """Test updating both gap and overlap settings."""
        result = self.manager.update_gap_settings(max_time_gap=240, min_time_overlap=45)
        
        assert result is True
        assert self.manager.time_slot_config["max_time_gap"] == 240
        assert self.manager.time_slot_config["min_time_overlap"] == 45
        
        # Check observer notification
        assert len(self.observer.notifications) == 1
        assert self.observer.notifications[0]['event_type'] == EventType.ROOMS_LOADED
    
    def test_update_gap_settings_gap_only(self):
        """Test updating only gap setting."""
        result = self.manager.update_gap_settings(max_time_gap=300)
        
        assert result is True
        assert self.manager.time_slot_config["max_time_gap"] == 300
        assert self.manager.time_slot_config["min_time_overlap"] == 30  # Unchanged
    
    def test_update_gap_settings_overlap_only(self):
        """Test updating only overlap setting."""
        result = self.manager.update_gap_settings(min_time_overlap=60)
        
        assert result is True
        assert self.manager.time_slot_config["max_time_gap"] == 180  # Unchanged
        assert self.manager.time_slot_config["min_time_overlap"] == 60
    
    def test_update_gap_settings_no_config(self):
        """Test updating gap settings when no configuration is loaded."""
        manager = TimeSlotManager()
        result = manager.update_gap_settings(max_time_gap=240)
        assert result is False
    
    def test_update_gap_settings_exception(self):
        """Test updating gap settings handles exceptions gracefully."""
        with patch.object(self.manager, 'notify_observers', side_effect=Exception("Test error")):
            result = self.manager.update_gap_settings(max_time_gap=240)
            assert result is False


class TestTimeSlotManagerSaveConfiguration:
    """Test configuration saving functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            "times": {"MON": [{"start": "08:00", "end": "09:50", "spacing": 60}]},
            "classes": [{"credits": 3, "meetings": [{"day": "MON", "duration": 110}]}]
        }
        self.manager = TimeSlotManager(time_slot_config=self.config)
        self.test_file = "test_config.json"
    
    def test_save_config_success(self):
        """Test successfully saving configuration to file."""
        existing_config = {"other_data": "preserved"}
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('json.dump') as mock_json_dump:
                result = self.manager.save_config(existing_config, self.test_file)
                
                assert result is True
                mock_file.assert_called_once_with(self.test_file, 'w', encoding='utf-8')
                mock_json_dump.assert_called_once()
                
                # Check that time slot config was added to existing config
                saved_config = mock_json_dump.call_args[0][0]
                assert saved_config["other_data"] == "preserved"
                assert saved_config["time_slot_config"] == self.config
    
    def test_save_config_no_time_slot_config(self):
        """Test saving when no time slot configuration is loaded."""
        manager = TimeSlotManager()
        result = manager.save_config({}, self.test_file)
        assert result is False
    
    def test_save_config_no_file_path(self):
        """Test saving with no file path provided."""
        result = self.manager.save_config({}, "")
        assert result is False
    
    def test_save_config_permission_error(self):
        """Test saving configuration handles permission errors."""
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            result = self.manager.save_config({}, self.test_file)
            assert result is False
    
    def test_save_config_file_not_found_error(self):
        """Test saving configuration handles file not found errors."""
        with patch('builtins.open', side_effect=FileNotFoundError("Directory not found")):
            result = self.manager.save_config({}, self.test_file)
            assert result is False
    
    def test_save_config_general_exception(self):
        """Test saving configuration handles general exceptions."""
        with patch('builtins.open', side_effect=Exception("General error")):
            result = self.manager.save_config({}, self.test_file)
            assert result is False
    
    def test_save_with_combined_config_success(self):
        """Test successfully saving with CombinedConfig."""
        mock_combined_config = Mock()
        
        with patch('scheduler.config.TimeSlotConfig') as mock_time_slot_config:
            mock_config_obj = Mock()
            mock_time_slot_config.return_value = mock_config_obj
            
            result = self.manager.save_with_combined_config(mock_combined_config)
            
            assert result is True
            mock_time_slot_config.assert_called_once_with(**self.config)
            assert mock_combined_config.time_slot_config == mock_config_obj
    
    def test_save_with_combined_config_no_config(self):
        """Test saving with CombinedConfig when no time slot config is loaded."""
        manager = TimeSlotManager()
        result = manager.save_with_combined_config(Mock())
        assert result is False
    
    def test_save_with_combined_config_none(self):
        """Test saving with None CombinedConfig."""
        result = self.manager.save_with_combined_config(None)
        assert result is False
    
    def test_save_with_combined_config_validation_error(self):
        """Test saving with CombinedConfig handles validation errors."""
        mock_combined_config = Mock()
        
        from pydantic import ValidationError as PydanticValidationError
        with patch('scheduler.config.TimeSlotConfig', side_effect=PydanticValidationError.from_exception_data('TimeSlotConfig', [])):
            result = self.manager.save_with_combined_config(mock_combined_config)
            assert result is False
    
    def test_save_with_combined_config_general_exception(self):
        """Test saving with CombinedConfig handles general exceptions."""
        mock_combined_config = Mock()
        
        with patch('scheduler.config.TimeSlotConfig', side_effect=Exception("General error")):
            result = self.manager.save_with_combined_config(mock_combined_config)
            assert result is False


class TestTimeSlotManagerValidation:
    """Test configuration validation functionality."""
    
    def test_validate_configuration_success(self):
        """Test validating a correct configuration."""
        config = {
            "times": {
                "MON": [{"start": "08:00", "end": "09:50"}],
                "TUE": [{"start": "10:00", "end": "11:50"}]
            },
            "classes": [
                {
                    "credits": 3,
                    "meetings": [{"day": "MON", "duration": 110}]
                }
            ]
        }
        manager = TimeSlotManager(time_slot_config=config)
        
        is_valid, errors = manager.validate_configuration()
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_configuration_no_config(self):
        """Test validating when no configuration is loaded."""
        manager = TimeSlotManager()
        
        is_valid, errors = manager.validate_configuration()
        
        assert is_valid is False
        assert "No time slot configuration loaded" in errors
    
    def test_validate_configuration_missing_times(self):
        """Test validating configuration missing times."""
        config = {"classes": []}
        manager = TimeSlotManager(time_slot_config=config)
        
        is_valid, errors = manager.validate_configuration()
        
        assert is_valid is False
        assert any("Missing required key: times" in error for error in errors)
    
    def test_validate_configuration_missing_classes(self):
        """Test validating configuration missing classes."""
        config = {"times": {}}
        manager = TimeSlotManager(time_slot_config=config)
        
        is_valid, errors = manager.validate_configuration()
        
        assert is_valid is False
        assert any("Missing required key: classes" in error for error in errors)
    
    def test_validate_configuration_invalid_times_type(self):
        """Test validating configuration with invalid times type."""
        config = {"times": "invalid", "classes": []}
        manager = TimeSlotManager(time_slot_config=config)
        
        is_valid, errors = manager.validate_configuration()
        
        assert is_valid is False
        assert any("'times' must be a dictionary" in error for error in errors)
    
    def test_validate_configuration_invalid_day(self):
        """Test validating configuration with invalid day."""
        config = {
            "times": {"INVALID": []},
            "classes": []
        }
        manager = TimeSlotManager(time_slot_config=config)
        
        is_valid, errors = manager.validate_configuration()
        
        assert is_valid is False
        assert any("Invalid day 'INVALID'" in error for error in errors)
    
    def test_validate_configuration_invalid_time_blocks_type(self):
        """Test validating configuration with invalid time blocks type."""
        config = {
            "times": {"MON": "invalid"},
            "classes": []
        }
        manager = TimeSlotManager(time_slot_config=config)
        
        is_valid, errors = manager.validate_configuration()
        
        assert is_valid is False
        assert any("Time blocks for MON must be a list" in error for error in errors)
    
    def test_validate_configuration_missing_start_time(self):
        """Test validating configuration with missing start time."""
        config = {
            "times": {"MON": [{"end": "09:50"}]},
            "classes": []
        }
        manager = TimeSlotManager(time_slot_config=config)
        
        is_valid, errors = manager.validate_configuration()
        
        assert is_valid is False
        assert any("missing 'start' time" in error for error in errors)
    
    def test_validate_configuration_missing_end_time(self):
        """Test validating configuration with missing end time."""
        config = {
            "times": {"MON": [{"start": "08:00"}]},
            "classes": []
        }
        manager = TimeSlotManager(time_slot_config=config)
        
        is_valid, errors = manager.validate_configuration()
        
        assert is_valid is False
        assert any("missing 'end' time" in error for error in errors)
    
    def test_validate_configuration_invalid_classes_type(self):
        """Test validating configuration with invalid classes type."""
        config = {
            "times": {},
            "classes": "invalid"
        }
        manager = TimeSlotManager(time_slot_config=config)
        
        is_valid, errors = manager.validate_configuration()
        
        assert is_valid is False
        assert any("'classes' must be a list" in error for error in errors)
    
    def test_validate_configuration_empty_classes(self):
        """Test validating configuration with empty classes."""
        config = {
            "times": {},
            "classes": []
        }
        manager = TimeSlotManager(time_slot_config=config)
        
        is_valid, errors = manager.validate_configuration()
        
        assert is_valid is False
        assert any("At least one class pattern must be defined" in error for error in errors)
    
    def test_validate_configuration_all_disabled_classes(self):
        """Test validating configuration with all disabled classes."""
        config = {
            "times": {},
            "classes": [
                {"credits": 3, "meetings": [{"day": "MON", "duration": 110}], "disabled": True}
            ]
        }
        manager = TimeSlotManager(time_slot_config=config)
        
        is_valid, errors = manager.validate_configuration()
        
        assert is_valid is False
        assert any("All class patterns are disabled" in error for error in errors)
    
    def test_validate_configuration_invalid_class_pattern_type(self):
        """Test validating configuration with invalid class pattern type."""
        config = {
            "times": {},
            "classes": ["invalid"]
        }
        manager = TimeSlotManager(time_slot_config=config)
        
        is_valid, errors = manager.validate_configuration()
        
        assert is_valid is False
        assert any("Class pattern 0 must be a dictionary" in error for error in errors)
    
    def test_validate_configuration_missing_credits(self):
        """Test validating configuration with missing credits."""
        config = {
            "times": {},
            "classes": [{"meetings": [{"day": "MON", "duration": 110}]}]
        }
        manager = TimeSlotManager(time_slot_config=config)
        
        is_valid, errors = manager.validate_configuration()
        
        assert is_valid is False
        assert any("missing 'credits'" in error for error in errors)
    
    def test_validate_configuration_missing_meetings(self):
        """Test validating configuration with missing meetings."""
        config = {
            "times": {},
            "classes": [{"credits": 3}]
        }
        manager = TimeSlotManager(time_slot_config=config)
        
        is_valid, errors = manager.validate_configuration()
        
        assert is_valid is False
        assert any("missing 'meetings'" in error for error in errors)
    
    def test_validate_configuration_invalid_meetings_type(self):
        """Test validating configuration with invalid meetings type."""
        config = {
            "times": {},
            "classes": [{"credits": 3, "meetings": "invalid"}]
        }
        manager = TimeSlotManager(time_slot_config=config)
        
        is_valid, errors = manager.validate_configuration()
        
        assert is_valid is False
        assert any("must have at least one meeting" in error for error in errors)
    
    def test_validate_configuration_empty_meetings(self):
        """Test validating configuration with empty meetings."""
        config = {
            "times": {},
            "classes": [{"credits": 3, "meetings": []}]
        }
        manager = TimeSlotManager(time_slot_config=config)
        
        is_valid, errors = manager.validate_configuration()
        
        assert is_valid is False
        assert any("must have at least one meeting" in error for error in errors)
    
    def test_validate_configuration_invalid_meeting_type(self):
        """Test validating configuration with invalid meeting type."""
        config = {
            "times": {},
            "classes": [{"credits": 3, "meetings": ["invalid"]}]
        }
        manager = TimeSlotManager(time_slot_config=config)
        
        is_valid, errors = manager.validate_configuration()
        
        assert is_valid is False
        assert any("meeting 0 must be a dictionary" in error for error in errors)
    
    def test_validate_configuration_missing_meeting_day(self):
        """Test validating configuration with missing meeting day."""
        config = {
            "times": {},
            "classes": [{"credits": 3, "meetings": [{"duration": 110}]}]
        }
        manager = TimeSlotManager(time_slot_config=config)
        
        is_valid, errors = manager.validate_configuration()
        
        assert is_valid is False
        assert any("missing 'day'" in error for error in errors)
    
    def test_validate_configuration_missing_meeting_duration(self):
        """Test validating configuration with missing meeting duration."""
        config = {
            "times": {},
            "classes": [{"credits": 3, "meetings": [{"day": "MON"}]}]
        }
        manager = TimeSlotManager(time_slot_config=config)
        
        is_valid, errors = manager.validate_configuration()
        
        assert is_valid is False
        assert any("missing 'duration'" in error for error in errors)


class TestTimeSlotManagerEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_time_slot_config_none_handling(self):
        """Test handling when time_slot_config is None."""
        manager = TimeSlotManager()
        
        # Test various methods with None config
        assert manager.get_time_blocks_for_day("MON") == []
        assert manager.get_all_days() == []
        assert manager.get_class_patterns() == []
        assert manager.get_enabled_class_patterns() == []
        assert manager.add_time_block("MON", {"start": "08:00", "end": "09:50"}) is False
        assert manager.remove_time_block("MON", 0) is False
        assert manager.modify_time_block("MON", 0, {"start": "08:00", "end": "09:50"}) is False
        assert manager.add_class_pattern({"credits": 3, "meetings": []}) is False
        assert manager.remove_class_pattern(0) is False
        assert manager.modify_class_pattern(0, {"credits": 3, "meetings": []}) is False
        assert manager.toggle_pattern_status(0) is False
        assert manager.update_gap_settings(max_time_gap=180) is False
    
    def test_time_slot_config_not_dict_handling(self):
        """Test handling when time_slot_config is not a dictionary."""
        manager = TimeSlotManager()
        # Simulate a corrupted config state
        manager.time_slot_config = "not a dict"
        
        is_valid, errors = manager.validate_configuration()
        assert is_valid is False
        # Should still handle gracefully without crashing
    
    def test_missing_times_key(self):
        """Test handling when 'times' key is missing from config."""
        manager = TimeSlotManager(time_slot_config={"classes": []})
        
        assert manager.get_time_blocks_for_day("MON") == []
        assert manager.get_all_days() == []
    
    def test_missing_classes_key(self):
        """Test handling when 'classes' key is missing from config."""
        manager = TimeSlotManager(time_slot_config={"times": {}})
        
        assert manager.get_class_patterns() == []
        assert manager.get_enabled_class_patterns() == []
    
    def test_observer_pattern_integration(self):
        """Test complete observer pattern integration."""
        manager = TimeSlotManager()
        observer1 = MockObserver()
        observer2 = MockObserver()
        
        # Add observers
        manager.add_observer(observer1)
        manager.add_observer(observer2)
        
        # Load configuration - should notify both observers
        config = {"times": {}, "classes": []}
        manager.load_time_slots(config)
        
        assert len(observer1.notifications) == 1
        assert len(observer2.notifications) == 1
        assert observer1.notifications[0]['event_type'] == EventType.COURSES_LOADED
        assert observer2.notifications[0]['event_type'] == EventType.COURSES_LOADED