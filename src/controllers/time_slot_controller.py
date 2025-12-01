"""Controller for time slot configuration management."""

from typing import List, Optional, Tuple
from src.models.time_slot_model import TimeSlotManager
from src.undo_manager import SnapshotUndoManager


class TimeSlotController:
    """Controller for managing time slot operations."""

    def __init__(self, manager: TimeSlotManager, undo_manager: Optional[SnapshotUndoManager] = None) -> None:
        """Initialize the controller with a time slot manager."""
        self.mgr = manager
        self.undo_manager = undo_manager

    def _record_change(self) -> None:
        """Record a snapshot if undo manager is attached."""
        if self.undo_manager is not None:
            self.undo_manager.record_change()

    def load_time_slots(self, time_slot_data: dict) -> None:
        """Load time slot configuration from data."""
        self.mgr.load_time_slots(time_slot_data)

    def get_time_slot_config(self):
        """Get the current time slot configuration."""
        return self.mgr.get_time_slot_config()

    def get_time_blocks_for_day(self, day: str) -> List[dict]:
        """Get all time blocks for a specific day."""
        return self.mgr.get_time_blocks_for_day(day)

    def get_daily_times_for_day(self, day: str) -> List[dict]:
        """Get daily time slots for a specific day (alias for get_time_blocks_for_day)."""
        return self.get_time_blocks_for_day(day)

    def get_all_days(self) -> List[str]:
        """Get all configured days."""
        return self.mgr.get_all_days()

    def get_class_patterns(self) -> List[dict]:
        """Get all class patterns."""
        return self.mgr.get_class_patterns()

    def get_enabled_class_patterns(self) -> List[dict]:
        """Get only enabled class patterns."""
        return self.mgr.get_enabled_class_patterns()

    def add_time_block(self, day: str, time_block_data: dict) -> bool:
        """Add a new time block to a specific day."""
        ok = self.mgr.add_time_block(day, time_block_data)
        if ok:
            self._record_change()
        return ok

    def modify_time_block(self, day: str, block_index: int,
                         new_data: dict) -> bool:
        """Modify an existing time block."""
        ok = self.mgr.modify_time_block(day, block_index, new_data)
        if ok:
            self._record_change()
        return ok

    def delete_time_block(self, day: str, block_index: int) -> bool:
        """Delete a time block from a specific day."""
        ok = self.mgr.remove_time_block(day, block_index)
        if ok:
            self._record_change()
        return ok

    def add_class_pattern(self, pattern_data: dict) -> bool:
        """Add a new class pattern."""
        ok = self.mgr.add_class_pattern(pattern_data)
        if ok:
            self._record_change()
        return ok

    def modify_class_pattern(self, pattern_index: int,
                            new_data: dict) -> bool:
        """Modify an existing class pattern."""
        ok = self.mgr.modify_class_pattern(pattern_index, new_data)
        if ok:
            self._record_change()
        return ok

    def delete_class_pattern(self, pattern_index: int) -> bool:
        """Delete a class pattern."""
        ok = self.mgr.remove_class_pattern(pattern_index)
        if ok:
            self._record_change()
        return ok

    def toggle_pattern_status(self, pattern_index: int) -> bool:
        """Toggle the enabled/disabled status of a class pattern."""
        ok = self.mgr.toggle_pattern_status(pattern_index)
        if ok:
            self._record_change()
        return ok

    def undo(self) -> bool:
        """Undo the last faculty change."""
        if self.undo_manager is None:
            return False
        return self.undo_manager.undo()

    def redo(self) -> bool:
        """Redo the last undone faculty change."""
        if self.undo_manager is None:
            return False
        return self.undo_manager.redo()

    def update_gap_settings(self, max_time_gap: Optional[int] = None,
                           min_time_overlap: Optional[int] = None) -> bool:
        """Update time gap and overlap settings."""
        ok = self.mgr.update_gap_settings(max_time_gap, min_time_overlap)
        if ok:
            self._record_change()
        return ok

    def validate_configuration(self) -> Tuple[bool, List[str]]:
        """Validate the current configuration."""
        return self.mgr.validate_configuration()

    def save_to_file(self, config: dict, config_file: str) -> bool:
        """Save to JSON file (CLI)."""
        return self.mgr.save_config(config, config_file)

    def save_to_combined_config(self, combined_config) -> bool:
        """Save to CombinedConfig (GUI)."""
        return self.mgr.save_with_combined_config(combined_config)

    # GUI compatibility methods (wrappers around main methods)
    def get_daily_times_for_day(self, day: str) -> List[dict]:
        """Get time blocks for a day (GUI compatibility)."""
        return self.get_time_blocks_for_day(day)

    def add_daily_time_slot(self, day: str, start: str, end: str, 
                           spacing: Optional[int] = None) -> bool:
        """Add daily time slot (GUI compatibility)."""
        time_block_data: dict = {"start": start, "end": end}
        if spacing is not None:
            time_block_data["spacing"] = spacing
        return self.add_time_block(day, time_block_data)

    def update_daily_time_slot(self, day: str, slot_index: int, start: str, 
                              end: str, spacing: Optional[int] = None) -> bool:
        """Update daily time slot (GUI compatibility)."""
        new_data: dict = {"start": start, "end": end}
        if spacing is not None:
            new_data["spacing"] = spacing
        return self.modify_time_block(day, slot_index, new_data)

    def delete_daily_time_slot(self, day: str, slot_index: int) -> bool:
        """Delete daily time slot (GUI compatibility)."""
        return self.delete_time_block(day, slot_index)

    def update_class_pattern(self, pattern_index: int, credits: int,
                            meetings: List[dict], disabled: bool = False,
                            start_time: Optional[str] = None) -> bool:
        """Update class pattern (GUI compatibility)."""
        new_pattern = {"credits": credits, "meetings": meetings}
        if disabled:
            new_pattern["disabled"] = disabled
        if start_time:
            new_pattern["start_time"] = start_time
        return self.modify_class_pattern(pattern_index, new_pattern)

    def run(self, config: dict, config_file: str) -> dict:
        """Main controller loop."""
        from src.views.cli.time_slot_view_cli import TimeSlotView
        
        # Load existing time slot configuration
        time_slot_data = config.get("time_slot_config", {})
        if time_slot_data:
            self.mgr.load_time_slots(time_slot_data)

        while True:
            TimeSlotView.show_menu()
            choice = TimeSlotView.get_menu_choice()

            if choice == "1":
                TimeSlotView.display_time_slots(self)
            elif choice == "2":
                TimeSlotView.manage_time_blocks(self)
            elif choice == "3":
                TimeSlotView.manage_class_patterns(self)
            elif choice == "4":
                TimeSlotView.configure_settings(self)
            elif choice == "5":
                success = self.mgr.save_config(config, config_file)
                if success:
                    msg = f"✅ Time slot configuration saved to {config_file}"
                    print(msg)
                    return config
                print("❌ Failed to save time slot configuration.")
                return config
            elif choice == "6":
                print("Exiting without saving changes.")
                return config
            elif choice == "7":
                if self.undo():
                    print("↩️ Successfully undid last change.")
                else:
                    print("❌ Nothing to undo.")
            elif choice == "8":
                if self.redo():
                    print("↪️ Successfully redid last change.")
                else:
                    print("❌ Nothing to redo.")
            else:
                print("❌ Invalid choice. Please select 1-8.")