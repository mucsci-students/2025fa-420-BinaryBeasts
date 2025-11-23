# src/controllers/timeslot_controller.py

from src.models.timeslot_model import TimeSlotManager
from typing import List, Dict, Any, Optional


class TimeSlotController:
    """Controller layer for time slot management - bridges view and model."""

    def __init__(self, manager: TimeSlotManager) -> None:
        """
        Initialize TimeSlotController.

        Args:
            manager: TimeSlotManager instance to control
        """
        self.mgr = manager

    def add_daily_time_slot(self, day: str, start: str, end: str, spacing: Optional[int] = None) -> bool:
        """
        Add a new daily time slot.

        Args:
            day: Day of the week (MON, TUE, WED, THU, FRI)
            start: Start time in HH:MM format
            end: End time in HH:MM format
            spacing: Optional spacing in minutes

        Returns:
            True if time slot was added, False otherwise
        """
        try:
            return self.mgr.add_daily_time_slot(day, start, end, spacing)
        except ValueError as e:
            raise e

    def delete_daily_time_slot(self, day: str, slot_index: int) -> bool:
        """
        Delete a daily time slot by index.

        Args:
            day: Day of the week
            slot_index: Index of the slot to delete

        Returns:
            True if slot was deleted, False if invalid index
        """
        return self.mgr.delete_daily_time_slot(day, slot_index)

    def update_daily_time_slot(self, day: str, slot_index: int, start: str, end: str, 
                              spacing: Optional[int] = None) -> bool:
        """
        Update an existing daily time slot.

        Args:
            day: Day of the week
            slot_index: Index of the slot to update
            start: New start time
            end: New end time
            spacing: New spacing in minutes

        Returns:
            True if slot was updated, False if invalid index
        """
        if day not in self.mgr.daily_times or slot_index < 0 or slot_index >= len(self.mgr.daily_times[day]):
            return False

        try:
            # Validate new time format
            if not self.mgr._is_valid_time_format(start) or not self.mgr._is_valid_time_format(end):
                raise ValueError("Invalid time format. Use HH:MM")

            # Update the slot
            old_slot = self.mgr.daily_times[day][slot_index].copy()
            new_slot = {"start": start, "end": end}
            if spacing is not None:
                new_slot["spacing"] = spacing
            
            self.mgr.daily_times[day][slot_index] = new_slot
            
            # Notify observers (reusing existing event type)
            from src.observer_pattern import EventType, EventData
            self.mgr.notify_observers(
                EventType.ROOM_UPDATED,
                EventData(
                    source=self.mgr,
                    old_value={"day": day, "index": slot_index, "slot": old_slot},
                    new_value={"day": day, "index": slot_index, "slot": new_slot}
                )
            )
            
            return True
        except ValueError as e:
            raise e

    def add_class_pattern(self, credits: int, meetings: List[Dict[str, Any]], 
                         disabled: bool = False, start_time: Optional[str] = None) -> bool:
        """
        Add a new class pattern.

        Args:
            credits: Number of credits for this pattern
            meetings: List of meeting dictionaries with day, duration, and optional lab
            disabled: Whether this pattern is disabled
            start_time: Optional fixed start time

        Returns:
            True if pattern was added
        """
        try:
            return self.mgr.add_class_pattern(credits, meetings, disabled, start_time)
        except ValueError as e:
            raise e

    def delete_class_pattern(self, pattern_index: int) -> bool:
        """
        Delete a class pattern by index.

        Args:
            pattern_index: Index of the pattern to delete

        Returns:
            True if pattern was deleted, False if invalid index
        """
        return self.mgr.delete_class_pattern(pattern_index)

    def update_class_pattern(self, pattern_index: int, credits: Optional[int] = None,
                           meetings: Optional[List[Dict[str, Any]]] = None,
                           disabled: Optional[bool] = None,
                           start_time: Optional[str] = None) -> bool:
        """
        Update an existing class pattern.

        Args:
            pattern_index: Index of the pattern to update
            credits: New credits value
            meetings: New meetings list
            disabled: New disabled status
            start_time: New start time

        Returns:
            True if pattern was updated, False if invalid index
        """
        try:
            return self.mgr.update_class_pattern(pattern_index, credits, meetings, disabled, start_time)
        except ValueError as e:
            raise e

    def get_daily_times(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all daily time slots."""
        return self.mgr.get_daily_times()

    def get_class_patterns(self) -> List[Dict[str, Any]]:
        """Get all class patterns."""
        return self.mgr.get_class_patterns()

    def get_daily_times_for_day(self, day: str) -> List[Dict[str, Any]]:
        """
        Get time slots for a specific day.

        Args:
            day: Day of the week (MON, TUE, WED, THU, FRI)

        Returns:
            List of time slots for the day
        """
        return self.mgr.daily_times.get(day, []).copy()

    def save_to_file(self, config: dict, time_slots: dict, config_file: str) -> bool:
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary
            time_slots: Time slots dictionary  
            config_file: Path to config file
            
        Returns:
            True if successful, False otherwise
        """
        return self.mgr.save_config(config, time_slots, config_file)

    def save_to_combined_config(self, combined_config) -> bool:
        """
        Save time slots back to CombinedConfig.

        Args:
            combined_config: CombinedConfig object to update

        Returns:
            True if save was successful
        """
        try:
            # Convert our data structure to the format expected by the scheduler
            time_slot_data = self.mgr.to_config_dict()
            
            # Update the CombinedConfig object
            with combined_config.edit_mode() as editable_config:
                # Update times
                for day, slots in time_slot_data["times"].items():
                    # Convert our dict format back to the scheduler's format
                    day_slots = []
                    for slot in slots:
                        # Create a simple object with the required attributes
                        class TimeSlot:
                            def __init__(self, start, end, spacing=None):
                                self.start = start
                                self.end = end
                                if spacing is not None:
                                    self.spacing = spacing
                        
                        time_slot = TimeSlot(slot["start"], slot["end"], slot.get("spacing"))
                        day_slots.append(time_slot)
                    
                    # Set the day's slots
                    if hasattr(editable_config.time_slot_config.times, day):
                        setattr(editable_config.time_slot_config.times, day, day_slots)
                
                # Update class patterns - this is more complex and may need scheduler library support
                # For now, we'll skip updating classes as it requires deep knowledge of scheduler internals
                
            return True
        except Exception:
            return False

    def validate_time_format(self, time_str: str) -> bool:
        """
        Validate time format.

        Args:
            time_str: Time string to validate

        Returns:
            True if valid format
        """
        return self.mgr._is_valid_time_format(time_str)

    def run(self, config: dict, config_file: str, time_slots: dict) -> dict:
        """
        Run time slot management operations and return updated config.
        
        Args:
            config: Current configuration dictionary
            config_file: Path to configuration file
            time_slots: Current time slots dictionary
            
        Returns:
            Updated configuration dictionary
        """
        # This method exists to maintain compatibility with other controllers
        # The actual management happens through the GUI dialog
        return config