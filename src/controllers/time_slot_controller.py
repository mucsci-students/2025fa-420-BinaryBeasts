"""Controller for time slot configuration management."""

from typing import List, Optional, Tuple
from src.models.time_slot_model import TimeSlotManager


class TimeSlotController:
    """Controller for managing time slot operations."""

    def __init__(self, manager: TimeSlotManager) -> None:
        """Initialize the controller with a time slot manager."""
        self.mgr = manager

    def load_time_slots(self, time_slot_data: dict) -> None:
        """Load time slot configuration from data."""
        self.mgr.load_time_slots(time_slot_data)

    def get_time_slot_config(self):
        """Get the current time slot configuration."""
        return self.mgr.get_time_slot_config()

    def get_time_blocks_for_day(self, day: str) -> List[dict]:
        """Get all time blocks for a specific day."""
        return self.mgr.get_time_blocks_for_day(day)

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
        return self.mgr.add_time_block(day, time_block_data)

    def modify_time_block(self, day: str, block_index: int,
                         new_data: dict) -> bool:
        """Modify an existing time block."""
        return self.mgr.modify_time_block(day, block_index, new_data)

    def delete_time_block(self, day: str, block_index: int) -> bool:
        """Delete a time block from a specific day."""
        return self.mgr.remove_time_block(day, block_index)

    def add_class_pattern(self, pattern_data: dict) -> bool:
        """Add a new class pattern."""
        return self.mgr.add_class_pattern(pattern_data)

    def modify_class_pattern(self, pattern_index: int,
                            new_data: dict) -> bool:
        """Modify an existing class pattern."""
        return self.mgr.modify_class_pattern(pattern_index, new_data)

    def delete_class_pattern(self, pattern_index: int) -> bool:
        """Delete a class pattern."""
        return self.mgr.remove_class_pattern(pattern_index)

    def toggle_pattern_status(self, pattern_index: int) -> bool:
        """Toggle the enabled/disabled status of a class pattern."""
        return self.mgr.toggle_pattern_status(pattern_index)

    def update_gap_settings(self, max_time_gap: Optional[int] = None,
                           min_time_overlap: Optional[int] = None) -> bool:
        """Update time gap and overlap settings."""
        return self.mgr.update_gap_settings(max_time_gap, min_time_overlap)

    def validate_configuration(self) -> Tuple[bool, List[str]]:
        """Validate the current configuration."""
        return self.mgr.validate_configuration()

    def save_to_file(self, config: dict, config_file: str) -> bool:
        """Save to JSON file (CLI)."""
        return self.mgr.save_config(config, config_file)

    def save_to_combined_config(self, combined_config) -> bool:
        """Save to CombinedConfig (GUI)."""
        return self.mgr.save_with_combined_config(combined_config)

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
            print("❌ Invalid choice. Please select 1-6.")