# src/models/timeslot_model.py

from typing import List, Dict, Any, Optional
from scheduler.config import CombinedConfig
from src.observer_pattern import Observable, EventType, EventData


class TimeSlotManager(Observable):
    """
    Time Slot Manager with Observer pattern support.
    
    Manages time slot configuration including daily time ranges and class meeting patterns.
    """

    def __init__(self, config: Optional[CombinedConfig] = None):
        """
        Initialize TimeSlotManager with Observer pattern support.

        Args:
            config: Optional CombinedConfig object. If provided, loads time slots from it.
        """
        Observable.__init__(self)  # Initialize observer pattern
        self.daily_times: Dict[str, List[Dict[str, Any]]] = {
            "MON": [], "TUE": [], "WED": [], "THU": [], "FRI": []
        }
        self.class_patterns: List[Dict[str, Any]] = []
        
        if config:
            self.load_time_slots(config)

    def load_time_slots(self, config: CombinedConfig) -> None:
        """
        Load time slots from a CombinedConfig object and notify observers.

        Args:
            config: CombinedConfig object containing time slot data
        """
        # Load daily time ranges
        if hasattr(config, "time_slot_config") and hasattr(config.time_slot_config, "times"):
            times = config.time_slot_config.times
            for day in self.daily_times.keys():
                # Support both object-style (attributes) and dict-style access safely
                if hasattr(times, day):
                    day_slots = getattr(times, day, [])
                elif isinstance(times, dict):
                    from typing import cast, Any
                    day_slots = cast(dict[str, Any], times).get(day, [])
                else:
                    day_slots = []
                self.daily_times[day] = []
                for slot in day_slots:
                    self.daily_times[day].append({
                        "start": slot.start,
                        "end": slot.end,
                        "spacing": getattr(slot, "spacing", None)
                    })
        
        # Load class patterns
        if hasattr(config, "time_slot_config") and hasattr(config.time_slot_config, "classes"):
            self.class_patterns = []
            for cls in config.time_slot_config.classes:
                pattern = {
                    "credits": cls.credits,
                    "meetings": []
                }
                
                # Add optional fields
                if hasattr(cls, "disabled"):
                    pattern["disabled"] = cls.disabled
                if hasattr(cls, "start_time"):
                    pattern["start_time"] = cls.start_time
                
                # Add meetings
                for meeting in cls.meetings:
                    meeting_dict = {
                        "day": meeting.day,
                        "duration": meeting.duration
                    }
                    if hasattr(meeting, "lab"):
                        meeting_dict["lab"] = meeting.lab
                    pattern["meetings"].append(meeting_dict)
                
                self.class_patterns.append(pattern)
        
        # Notify observers that time slots have been loaded
        self.notify_observers(
            EventType.ROOMS_LOADED,  # We can reuse this or create new event type
            EventData(
                source=self,
                new_value={"daily_times": self.daily_times, "class_patterns": self.class_patterns},
                count=len(self.class_patterns)
            )
        )

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
        if day not in self.daily_times:
            raise ValueError(f"Invalid day: {day}")

        if not self._is_valid_time_format(start) or not self._is_valid_time_format(end):
            raise ValueError("Invalid time format. Use HH:MM")

        new_slot = {"start": start, "end": end}
        if spacing is not None:
            new_slot["spacing"] = spacing

        # Check for conflicts with existing slots
        if self._has_time_conflict(day, start, end):
            return False

        self.daily_times[day].append(new_slot)
        
        # Notify observers
        self.notify_observers(
            EventType.ROOM_ADDED,  # Reusing existing event type or create new one
            EventData(
                source=self,
                new_value={"day": day, "slot": new_slot},
                total_rooms=len(self.daily_times[day])
            )
        )
        
        return True

    def delete_daily_time_slot(self, day: str, slot_index: int) -> bool:
        """
        Delete a daily time slot by index.

        Args:
            day: Day of the week
            slot_index: Index of the slot to delete

        Returns:
            True if slot was deleted, False if invalid index
        """
        if day not in self.daily_times or slot_index < 0 or slot_index >= len(self.daily_times[day]):
            return False

        removed_slot = self.daily_times[day].pop(slot_index)
        
        # Notify observers
        self.notify_observers(
            EventType.ROOM_REMOVED,  # Reusing existing event type
            EventData(
                source=self,
                old_value={"day": day, "slot": removed_slot},
                total_rooms=len(self.daily_times[day])
            )
        )
        
        return True

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
        pattern = {
            "credits": credits,
            "meetings": meetings.copy()
        }
        
        if disabled:
            pattern["disabled"] = disabled
        if start_time:
            pattern["start_time"] = start_time

        self.class_patterns.append(pattern)
        
        # Notify observers
        self.notify_observers(
            EventType.ROOM_ADDED,  # Reusing existing event type
            EventData(
                source=self,
                new_value=pattern,
                total_rooms=len(self.class_patterns)
            )
        )
        
        return True

    def delete_class_pattern(self, pattern_index: int) -> bool:
        """
        Delete a class pattern by index.

        Args:
            pattern_index: Index of the pattern to delete

        Returns:
            True if pattern was deleted, False if invalid index
        """
        if pattern_index < 0 or pattern_index >= len(self.class_patterns):
            return False

        removed_pattern = self.class_patterns.pop(pattern_index)
        
        # Notify observers
        self.notify_observers(
            EventType.ROOM_REMOVED,  # Reusing existing event type
            EventData(
                source=self,
                old_value=removed_pattern,
                total_rooms=len(self.class_patterns)
            )
        )
        
        return True

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
        if pattern_index < 0 or pattern_index >= len(self.class_patterns):
            return False

        pattern = self.class_patterns[pattern_index]
        old_pattern = pattern.copy()

        if credits is not None:
            pattern["credits"] = credits
        if meetings is not None:
            pattern["meetings"] = meetings.copy()
        if disabled is not None:
            pattern["disabled"] = disabled
        if start_time is not None:
            pattern["start_time"] = start_time

        # Notify observers
        self.notify_observers(
            EventType.ROOM_UPDATED,  # Assuming this event type exists
            EventData(
                source=self,
                old_value=old_pattern,
                new_value=pattern,
                index=pattern_index
            )
        )
        
        return True

    def get_daily_times(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all daily time slots."""
        return self.daily_times.copy()

    def get_class_patterns(self) -> List[Dict[str, Any]]:
        """Get all class patterns."""
        return [pattern.copy() for pattern in self.class_patterns]

    def _is_valid_time_format(self, time_str: str) -> bool:
        """
        Validate time format (HH:MM).

        Args:
            time_str: Time string to validate

        Returns:
            True if valid format
        """
        try:
            parts = time_str.split(":")
            if len(parts) != 2:
                return False
            
            hour = int(parts[0])
            minute = int(parts[1])
            
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except (ValueError, AttributeError):
            return False

    def _has_time_conflict(self, day: str, start: str, end: str) -> bool:
        """
        Check if a new time slot conflicts with existing slots.

        Args:
            day: Day of the week
            start: Start time
            end: End time

        Returns:
            True if there's a conflict
        """
        def time_to_minutes(time_str: str) -> int:
            parts = time_str.split(":")
            return int(parts[0]) * 60 + int(parts[1])

        new_start_min = time_to_minutes(start)
        new_end_min = time_to_minutes(end)

        for slot in self.daily_times[day]:
            existing_start_min = time_to_minutes(slot["start"])
            existing_end_min = time_to_minutes(slot["end"])

            # Check for overlap
            if (new_start_min < existing_end_min and new_end_min > existing_start_min):
                return True

        return False

    def to_config_dict(self) -> Dict[str, Any]:
        """
        Convert time slot data to configuration dictionary format.

        Returns:
            Dictionary suitable for saving to config file
        """
        return {
            "times": self.daily_times.copy(),
            "classes": [pattern.copy() for pattern in self.class_patterns]
        }

    def save_config(self, config: dict, time_slots: dict, config_file: str) -> bool:
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary
            time_slots: Time slots dictionary  
            config_file: Path to config file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import json
            full_config = {"config": config, "time_slot_config": time_slots}
            with open(config_file, 'w') as f:
                json.dump(full_config, f, indent=2)
            return True
        except Exception:
            return False