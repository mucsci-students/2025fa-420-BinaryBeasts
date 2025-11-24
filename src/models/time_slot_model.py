"""
Time slot model module.

Provides TimeSlotManager class for managing time slot configurations with
observer pattern support and Pydantic validation.
"""

import json
import copy
from typing import List, Optional
from pydantic import ValidationError
from src.observer_pattern import Observable, EventType, EventData
from scheduler.config import CombinedConfig


class TimeSlotManager(Observable):
    """
    Time Slot Manager with Observer pattern support.

    This class manages time slot configuration data and notifies observers when
    time slots, patterns, or settings are modified.
    """

    def __init__(self, time_slot_config=None) -> None:
        """Initialize the TimeSlotManager."""
        Observable.__init__(self)  # Initialize observer pattern
        self.time_slot_config = time_slot_config
        self._original_config: Optional[dict] = None

    def load_time_slots(self, time_slot_data: dict) -> None:
        """Load time slot configuration from data."""
        try:
            # Validate the basic structure
            if not isinstance(time_slot_data, dict):
                raise ValueError("Time slot data must be a dictionary")

            # Store the configuration
            self.time_slot_config = time_slot_data
            self._original_config = time_slot_data.copy()

            # Notify observers
            self.notify_observers(
                EventType.COURSES_LOADED,  # Using existing event type
                EventData(data={"time_slot_config": time_slot_data})
            )
        except Exception as e:
            raise ValueError(f"Failed to load time slot configuration: {e}")

    def get_time_slot_config(self):
        """Get the current time slot configuration."""
        return self.time_slot_config

    def get_time_blocks_for_day(self, day: str) -> List[dict]:
        """Get all time blocks for a specific day."""
        if not self.time_slot_config or "times" not in self.time_slot_config:
            return []
        return self.time_slot_config["times"].get(day, [])

    def get_all_days(self) -> List[str]:
        """Get all configured days."""
        if not self.time_slot_config or "times" not in self.time_slot_config:
            return []
        return list(self.time_slot_config["times"].keys())

    def get_class_patterns(self) -> List[dict]:
        """Get all class patterns."""
        if not self.time_slot_config or "classes" not in self.time_slot_config:
            return []
        return self.time_slot_config["classes"]

    def get_enabled_class_patterns(self) -> List[dict]:
        """Get only enabled class patterns."""
        patterns = self.get_class_patterns()
        return [pattern for pattern in patterns
                if not pattern.get("disabled", False)]

    def add_time_block(self, day: str, time_block: dict) -> bool:
        """Add a time block to a specific day."""
        if not self.time_slot_config:
            return False

        try:
            if "times" not in self.time_slot_config:
                self.time_slot_config["times"] = {}

            if day not in self.time_slot_config["times"]:
                self.time_slot_config["times"][day] = []

            # Validate required fields
            required_fields = ["start", "end"]
            for field in required_fields:
                if field not in time_block:
                    raise ValueError(f"Missing required field: {field}")

            # Ensure spacing field is present (required by TimeSlotConfig)
            if "spacing" not in time_block:
                time_block["spacing"] = 60  # Default spacing of 60 minutes

            # Insert in chronological order if start times are comparable
            time_blocks = self.time_slot_config["times"][day]
            time_blocks.append(time_block)

            # Notify observers
            self.notify_observers(
                EventType.COURSE_ADDED,  # Using existing event type
                EventData(data={"day": day, "time_block": time_block})
            )
            return True
        except Exception:
            return False

    def remove_time_block(self, day: str, block_index: int) -> bool:
        """Remove a time block from a specific day."""
        if not self.time_slot_config or "times" not in self.time_slot_config:
            return False

        if day not in self.time_slot_config["times"]:
            return False

        try:
            time_blocks = self.time_slot_config["times"][day]
            if 0 <= block_index < len(time_blocks):
                removed_block = time_blocks.pop(block_index)

                # Notify observers
                data = {
                    "day": day,
                    "block_index": block_index,
                    "removed_block": removed_block
                }
                self.notify_observers(
                    EventType.COURSE_REMOVED,  # Using existing event type
                    EventData(data=data)
                )
                return True
        except Exception:
            pass
        return False

    def modify_time_block(self, day: str, block_index: int,
                         new_time_block: dict) -> bool:
        """Modify an existing time block."""
        if not self.time_slot_config or "times" not in self.time_slot_config:
            return False

        if day not in self.time_slot_config["times"]:
            return False

        try:
            time_blocks = self.time_slot_config["times"][day]
            if 0 <= block_index < len(time_blocks):
                old_block = time_blocks[block_index]

                # Ensure spacing field is present (required by TimeSlotConfig)
                if "spacing" not in new_time_block:
                    new_time_block["spacing"] = old_block.get("spacing", 60)

                time_blocks[block_index] = new_time_block

                # Notify observers
                data = {
                    "day": day,
                    "block_index": block_index,
                    "old_block": old_block,
                    "new_block": new_time_block
                }
                self.notify_observers(
                    EventType.COURSE_UPDATED,  # Using existing event type
                    EventData(data=data)
                )
                return True
        except Exception:
            pass
        return False

    def add_class_pattern(self, pattern: dict) -> bool:
        """Add a new class pattern."""
        if not self.time_slot_config:
            return False

        try:
            if "classes" not in self.time_slot_config:
                self.time_slot_config["classes"] = []

            # Validate required fields
            required_fields = ["credits", "meetings"]
            for field in required_fields:
                if field not in pattern:
                    raise ValueError(f"Missing required field: {field}")

            # Validate meetings structure
            meetings = pattern.get("meetings", [])
            if not meetings:
                raise ValueError("At least one meeting must be specified")

            for meeting in meetings:
                if "day" not in meeting or "duration" not in meeting:
                    msg = "Each meeting must have 'day' and 'duration' fields"
                    raise ValueError(msg)

            self.time_slot_config["classes"].append(pattern)

            # Notify observers
            self.notify_observers(
                EventType.LAB_ADDED,  # Using existing event type
                EventData(data={"class_pattern": pattern})
            )
            return True
        except Exception:
            return False

    def remove_class_pattern(self, pattern_index: int) -> bool:
        """Remove a class pattern."""
        if not self.time_slot_config or "classes" not in self.time_slot_config:
            return False

        try:
            if 0 <= pattern_index < len(self.time_slot_config["classes"]):
                removed_pattern = self.time_slot_config["classes"].pop(
                    pattern_index)

                # Notify observers
                data = {
                    "pattern_index": pattern_index,
                    "removed_pattern": removed_pattern
                }
                self.notify_observers(
                    EventType.LAB_REMOVED,  # Using existing event type
                    EventData(data=data)
                )
                return True
        except Exception:
            pass
        return False

    def modify_class_pattern(self, pattern_index: int,
                           new_pattern: dict) -> bool:
        """Modify an existing class pattern."""
        if not self.time_slot_config or "classes" not in self.time_slot_config:
            return False

        try:
            if 0 <= pattern_index < len(self.time_slot_config["classes"]):
                old_pattern = self.time_slot_config["classes"][pattern_index]
                self.time_slot_config["classes"][pattern_index] = new_pattern

                # Notify observers
                data = {
                    "pattern_index": pattern_index,
                    "old_pattern": old_pattern,
                    "new_pattern": new_pattern
                }
                self.notify_observers(
                    EventType.LAB_UPDATED,  # Using existing event type
                    EventData(data=data)
                )
                return True
        except Exception:
            pass
        return False

    def toggle_pattern_status(self, pattern_index: int) -> bool:
        """Toggle the enabled/disabled status of a class pattern."""
        if not self.time_slot_config or "classes" not in self.time_slot_config:
            return False

        try:
            if 0 <= pattern_index < len(self.time_slot_config["classes"]):
                pattern = self.time_slot_config["classes"][pattern_index]
                old_status = pattern.get("disabled", False)
                pattern["disabled"] = not old_status

                # Notify observers
                data = {
                    "pattern_index": pattern_index,
                    "old_status": old_status,
                    "new_status": pattern["disabled"]
                }
                self.notify_observers(
                    EventType.FACULTY_UPDATED,  # Using existing event type
                    EventData(data=data)
                )
                return True
        except Exception:
            pass
        return False

    def update_gap_settings(self, max_time_gap: Optional[int] = None,
                           min_time_overlap: Optional[int] = None) -> bool:
        """Update time gap and overlap settings."""
        if not self.time_slot_config:
            return False

        try:
            old_gap = self.time_slot_config.get("max_time_gap")
            old_overlap = self.time_slot_config.get("min_time_overlap")

            if max_time_gap is not None:
                self.time_slot_config["max_time_gap"] = max_time_gap
            if min_time_overlap is not None:
                self.time_slot_config["min_time_overlap"] = min_time_overlap

            # Notify observers
            data = {
                "old_gap": old_gap,
                "new_gap": self.time_slot_config.get("max_time_gap"),
                "old_overlap": old_overlap,
                "new_overlap": self.time_slot_config.get("min_time_overlap")
            }
            self.notify_observers(
                EventType.ROOMS_LOADED,  # Using existing event type
                EventData(data=data)
            )
            return True
        except Exception:
            return False

    def save_config(self, config: dict, config_file: str) -> bool:
        """Save time slot configuration to file."""
        if not self.time_slot_config:
            print("❌ No time slot configuration to save")
            return False

        if not config_file:
            print("❌ No configuration file path provided")
            return False

        try:
            # Update the config with current time slot data
            config["time_slot_config"] = self.time_slot_config

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            return True
        except PermissionError:
            print(f"❌ Permission denied: Cannot write to {config_file}")
            return False
        except FileNotFoundError:
            print(f"❌ Directory not found for {config_file}")
            return False
        except Exception as e:
            print(f"❌ Error saving time slot configuration: {e}")
            return False

    def save_with_combined_config(self, combined_config: CombinedConfig) -> bool:
        """Save time slot configuration using CombinedConfig."""
        if not self.time_slot_config:
            print("❌ No time slot configuration to save")
            return False

        if combined_config is None:
            print("❌ No configuration object provided")
            return False

        try:
            # Import TimeSlotConfig to convert our dict to proper object
            from scheduler.config import TimeSlotConfig

            # Convert our dict configuration to a TimeSlotConfig object
            time_slot_config_obj = TimeSlotConfig(**self.time_slot_config)

            # Update the time slot configuration directly
            combined_config.time_slot_config = time_slot_config_obj
            return True
        except ValidationError as e:
            print(f"❌ Configuration validation error: {e}")
            msg = "   This usually means required fields are missing"
            msg += " or have invalid values."
            print(msg)
            return False
        except Exception as e:
            print(f"❌ Error saving time slot configuration: {e}")
            return False

    def validate_configuration(self) -> tuple[bool, List[str]]:
        """
        Validate the current configuration and return status and any errors.

        Returns:
            tuple: (is_valid, list_of_errors)
        """
        if not self.time_slot_config:
            return False, ["No time slot configuration loaded"]

        errors = []

        # Check for required top-level keys
        required_keys = ["times", "classes"]
        for key in required_keys:
            if key not in self.time_slot_config:
                errors.append(f"Missing required key: {key}")

        # Validate times structure
        if "times" in self.time_slot_config:
            errors.extend(self._validate_times_structure())

        # Validate classes structure
        if "classes" in self.time_slot_config:
            errors.extend(self._validate_classes_structure())

        return len(errors) == 0, errors

    def _validate_times_structure(self) -> List[str]:
        """Validate the times structure and return errors."""
        errors = []
        # Safely access 'times' — time_slot_config may be None or not a dict
        times = {}
        if isinstance(self.time_slot_config, dict):
            times = self.time_slot_config.get("times", {})

        if not isinstance(times, dict):
            errors.append("'times' must be a dictionary")
        else:
            valid_days = {"MON", "TUE", "WED", "THU", "FRI"}
            for day, blocks in times.items():
                if day not in valid_days:
                    msg = f"Invalid day '{day}' in time slot configuration"
                    errors.append(msg)
                if not isinstance(blocks, list):
                    errors.append(f"Time blocks for {day} must be a list")
                else:
                    errors.extend(
                        self._validate_time_blocks(day, blocks))
        return errors

    def _validate_time_blocks(self, day: str, blocks: List[dict]) -> List[str]:
        """Validate time blocks for a given day."""
        errors = []
        for i, block in enumerate(blocks):
            if not isinstance(block, dict):
                msg = f"Time block {i} for {day} must be a dictionary"
                errors.append(msg)
            else:
                if "start" not in block:
                    msg = f"Time block {i} for {day} missing 'start' time"
                    errors.append(msg)
                if "end" not in block:
                    msg = f"Time block {i} for {day} missing 'end' time"
                    errors.append(msg)
        return errors

    def _validate_classes_structure(self) -> List[str]:
        """Validate the classes structure and return errors."""
        errors = []
        # Safely access 'classes' — time_slot_config may be None or not a dict
        classes = []
        if isinstance(self.time_slot_config, dict):
            classes = self.time_slot_config.get("classes", [])

        if not isinstance(classes, list):
            errors.append("'classes' must be a list")
        else:
            if not classes:
                errors.append("At least one class pattern must be defined")
            else:
                # Check for all disabled patterns
                enabled_patterns = [p for p in classes
                                  if not p.get("disabled", False)]
                if not enabled_patterns:
                    errors.append("All class patterns are disabled")

            for i, pattern in enumerate(classes):
                errors.extend(self._validate_class_pattern(i, pattern))
        return errors

    def _validate_class_pattern(self, i: int, pattern: dict) -> List[str]:
        """Validate a single class pattern."""
        errors = []
        if not isinstance(pattern, dict):
            errors.append(f"Class pattern {i} must be a dictionary")
        else:
            # Check for required fields in new format
            required_pattern_fields = ["credits", "meetings"]
            for field in required_pattern_fields:
                if field not in pattern:
                    errors.append(f"Class pattern {i} missing '{field}'")

            # Validate meetings structure
            if "meetings" in pattern:
                errors.extend(self._validate_meetings(i, pattern["meetings"]))
        return errors

    def _validate_meetings(self, pattern_index: int,
                          meetings: List[dict]) -> List[str]:
        """Validate meetings structure for a class pattern."""
        errors = []
        if not isinstance(meetings, list) or not meetings:
            msg = f"Class pattern {pattern_index} must have at least one meeting"
            errors.append(msg)
        else:
            for j, meeting in enumerate(meetings):
                if not isinstance(meeting, dict):
                    msg = (f"Class pattern {pattern_index}, meeting {j} "
                           "must be a dictionary")
                    errors.append(msg)
                else:
                    for meeting_field in ["day", "duration"]:
                        if meeting_field not in meeting:
                            msg = (f"Class pattern {pattern_index}, "
                                   f"meeting {j} missing '{meeting_field}'")
                            errors.append(msg)
        return errors

    def snapshot_state(self) -> dict:
        """Return a snapshot of the current time slot configuration."""
        # Deep copy so undo/redo doesn't share references
        if self.time_slot_config is None:
            return {}
        return copy.deepcopy(self.time_slot_config)

    def restore_state(self, state: dict) -> None:
        """Restore state from a snapshot."""
        # Deep copy again to avoid aliasing
        self.time_slot_config = copy.deepcopy(state)
