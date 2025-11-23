"""Time slot configuration CLI view module.

Provides command-line interface for managing time slot configurations,
including time blocks, class patterns, and scheduling settings.
"""
from src.controllers.time_slot_controller import TimeSlotController


class TimeSlotView:
    """CLI view for time slot configuration management."""
    @staticmethod
    def show_menu() -> None:
        """Display the main menu."""
        print("\n" + "=" * 60)
        print("TIME SLOT CONFIGURATION MANAGEMENT")
        print("=" * 60)
        print("1. 👀 View time slot configuration")
        print("2. 🕐 Manage time blocks")
        print("3. 📅 Manage class patterns")
        print("4. ⚙️  Configure settings")
        print("5. 💾 Save changes and exit")
        print("6. 🚪 Exit without saving")
        print("=" * 60)

    @staticmethod
    def get_menu_choice() -> str:
        """Get user's menu choice."""
        return input("Select an option (1-6): ").strip()

    @staticmethod
    def display_time_slots(controller: TimeSlotController) -> None:
        """Display the current time slot configuration."""
        print("\n" + "=" * 80)
        print("TIME SLOT CONFIGURATION")
        print("=" * 80)

        config = controller.get_time_slot_config()
        if not config:
            print("No time slot configuration loaded.")
            return

        # Display each section
        TimeSlotView._display_time_blocks_section(controller)
        TimeSlotView._display_class_patterns_section(controller)
        TimeSlotView._display_settings_section(config)

        print("=" * 80)

    @staticmethod
    def _display_time_blocks_section(controller: TimeSlotController) -> None:
        """Display time blocks section."""
        print("\n📅 TIME BLOCKS BY DAY:")
        print("-" * 50)
        days = controller.get_all_days()
        if not days:
            print("No time blocks configured.")
        else:
            for day in sorted(days):
                time_blocks = controller.get_time_blocks_for_day(day)
                print(f"\n🗓️  {day}:")
                if not time_blocks:
                    print("   No time blocks configured")
                else:
                    for i, block in enumerate(time_blocks):
                        start = block.get("start", "N/A")
                        end = block.get("end", "N/A")
                        spacing = block.get("spacing", "N/A")
                        print(f"   {i + 1}. {start} - {end} (spacing: {spacing})")

    @staticmethod
    def _display_class_patterns_section(controller: TimeSlotController) -> None:
        """Display class patterns section."""
        print("\n📝 CLASS PATTERNS:")
        print("-" * 50)
        patterns = controller.get_class_patterns()
        if not patterns:
            print("No class patterns configured.")
        else:
            for i, pattern in enumerate(patterns):
                TimeSlotView._display_single_pattern(i, pattern)

    @staticmethod
    def _display_single_pattern(index: int, pattern: dict) -> None:
        """Display a single class pattern."""
        pattern_credits = pattern.get("credits", "N/A")
        disabled = pattern.get("disabled", False)

        # Extract data from meetings array
        meetings = pattern.get("meetings", [])
        days = [meeting.get("day", "") for meeting in meetings
               if meeting.get("day")]
        durations = [meeting.get("duration", 0) for meeting in meetings]
        duration = durations[0] if durations else "N/A"
        lab = any(meeting.get("lab", False) for meeting in meetings)

        start_time = pattern.get("start_time")

        status = "🔴 Disabled" if disabled else "🟢 Enabled"
        pattern_type = "🔬 Lab" if lab else "📚 Regular"

        print(f"\n   {index + 1}. {pattern_type} Pattern - "
              f"{pattern_credits} credits ({status})")
        print(f"      Days: {', '.join(days) if days else 'None'}")
        print(f"      Duration: {duration} minutes")

        if start_time:
            print(f"      Fixed start time: {start_time}")

    @staticmethod
    def _display_settings_section(config: dict) -> None:
        """Display settings section."""
        print("\n⚙️ CONFIGURATION SETTINGS:")
        print("-" * 50)
        max_gap = config.get("max_time_gap", "Not set")
        min_overlap = config.get("min_time_overlap", "Not set")
        print(f"   Max time gap: {max_gap}")
        print(f"   Min time overlap: {min_overlap}")

    @staticmethod
    def manage_time_blocks(controller: TimeSlotController) -> None:
        """Manage time blocks for days."""
        while True:
            print("\n" + "=" * 50)
            print("TIME BLOCK MANAGEMENT")
            print("=" * 50)
            print("1. 👀 View time blocks")
            print("2. ➕ Add time block")
            print("3. ✏️  Modify time block")
            print("4. ❌ Delete time block")
            print("5. 🔙 Back to main menu")
            print("=" * 50)

            choice = input("Select an option (1-5): ").strip()

            if choice == "1":
                TimeSlotView._display_time_blocks_only(controller)
            elif choice == "2":
                TimeSlotView._add_time_block_interactive(controller)
            elif choice == "3":
                TimeSlotView._modify_time_block_interactive(controller)
            elif choice == "4":
                TimeSlotView._delete_time_block_interactive(controller)
            elif choice == "5":
                break
            else:
                print("❌ Invalid choice. Please select 1-5.")

    @staticmethod
    def manage_class_patterns(controller: TimeSlotController) -> None:
        """Manage class patterns."""
        while True:
            print("\n" + "=" * 50)
            print("CLASS PATTERN MANAGEMENT")
            print("=" * 50)
            print("1. 👀 View class patterns")
            print("2. ➕ Add class pattern")
            print("3. ✏️  Modify class pattern")
            print("4. ❌ Delete class pattern")
            print("5. 🔄 Toggle pattern status")
            print("6. 🔙 Back to main menu")
            print("=" * 50)

            choice = input("Select an option (1-6): ").strip()

            if choice == "1":
                TimeSlotView._display_class_patterns_only(controller)
            elif choice == "2":
                TimeSlotView._add_class_pattern_interactive(controller)
            elif choice == "3":
                TimeSlotView._modify_class_pattern_interactive(controller)
            elif choice == "4":
                TimeSlotView._delete_class_pattern_interactive(controller)
            elif choice == "5":
                TimeSlotView._toggle_pattern_status_interactive(controller)
            elif choice == "6":
                break
            else:
                print("❌ Invalid choice. Please select 1-6.")

    @staticmethod
    def configure_settings(controller: TimeSlotController) -> None:
        """Configure time gap and overlap settings."""
        print("\n" + "=" * 50)
        print("CONFIGURATION SETTINGS")
        print("=" * 50)

        config = controller.get_time_slot_config()
        if config:
            current_gap = config.get("max_time_gap", "Not set")
            current_overlap = config.get("min_time_overlap", "Not set")
            print(f"Current max time gap: {current_gap}")
            print(f"Current min time overlap: {current_overlap}")

        print("\nEnter new values (press Enter to keep current):")

        # Get max time gap
        gap_input = input("Max time gap (minutes): ").strip()
        max_gap = None
        if gap_input:
            try:
                max_gap = int(gap_input)
                if max_gap < 0:
                    print("❌ Time gap must be non-negative.")
                    return
            except ValueError:
                print("❌ Invalid number for time gap.")
                return

        # Get min time overlap
        overlap_input = input("Min time overlap (minutes): ").strip()
        min_overlap = None
        if overlap_input:
            try:
                min_overlap = int(overlap_input)
                if min_overlap <= 0:
                    print("❌ Time overlap must be positive.")
                    return
            except ValueError:
                print("❌ Invalid number for time overlap.")
                return

        if max_gap is not None or min_overlap is not None:
            if controller.update_gap_settings(max_gap, min_overlap):
                print("✅ Settings updated successfully.")
            else:
                print("❌ Failed to update settings.")
        else:
            print("No changes made.")

    # Helper methods for time block management
    @staticmethod
    def _display_time_blocks_only(controller: TimeSlotController) -> None:
        """Display only time blocks."""
        days = controller.get_all_days()
        if not days:
            print("No time blocks configured.")
            return

        for day in sorted(days):
            time_blocks = controller.get_time_blocks_for_day(day)
            print(f"\n🗓️  {day}:")
            if not time_blocks:
                print("   No time blocks configured")
            else:
                for i, block in enumerate(time_blocks):
                    start = block.get("start", "N/A")
                    end = block.get("end", "N/A")
                    spacing = block.get("spacing", "N/A")
                    print(f"   {i + 1}. {start} - {end} (spacing: {spacing})")

    @staticmethod
    def _add_time_block_interactive(controller: TimeSlotController) -> None:
        """Add a time block interactively."""
        print("\n🆕 ADD NEW TIME BLOCK")
        print("=" * 30)

        # Get day
        day = input("Day (MON, TUE, WED, THU, FRI): ").strip().upper()
        if day not in ["MON", "TUE", "WED", "THU", "FRI"]:
            print("❌ Invalid day. Must be MON, TUE, WED, THU, or FRI.")
            return

        # Get start time
        start_time = input("Start time (HH:MM format): ").strip()
        if not start_time:
            print("❌ Start time cannot be empty.")
            return

        # Get end time
        end_time = input("End time (HH:MM format): ").strip()
        if not end_time:
            print("❌ End time cannot be empty.")
            return

        # Get spacing (required)
        while True:
            spacing_input = input("Spacing in minutes (default 60): ").strip()
            if not spacing_input:
                spacing = 60  # Default value
                break
            try:
                spacing = int(spacing_input)
                if spacing <= 0:
                    print("❌ Spacing must be greater than 0.")
                    continue
                break
            except ValueError:
                print("❌ Invalid spacing. Must be a number.")
                continue

        # Create time block data
        time_block_data = {
            "start": start_time,
            "end": end_time,
            "spacing": spacing
        }

        # Add the time block
        if controller.add_time_block(day, time_block_data):
            print(f"✅ Successfully added time block for {day}")
        else:
            print("❌ Failed to add time block.")

    @staticmethod
    def _modify_time_block_interactive(controller: TimeSlotController) -> None:
        """Modify a time block interactively."""
        TimeSlotView._display_time_blocks_only(controller)

        day = input("\nEnter day to modify (MON, TUE, WED, THU, FRI): ").strip().upper()
        if day not in ["MON", "TUE", "WED", "THU", "FRI"]:
            print("❌ Invalid day.")
            return

        time_blocks = controller.get_time_blocks_for_day(day)
        if not time_blocks:
            print(f"❌ No time blocks found for {day}.")
            return

        try:
            index = int(input("Enter time block number to modify: ")) - 1
            if index < 0 or index >= len(time_blocks):
                print("❌ Invalid time block number.")
                return
        except ValueError:
            print("❌ Invalid number.")
            return

        current_block = time_blocks[index]
        print(f"\nModifying time block {index + 1} for {day}")
        print(f"Current: {current_block.get('start')} - {current_block.get('end')}")

        # Get new values
        start_input = input(f"New start time (current: {current_block.get('start')}): ").strip()
        start_time = start_input if start_input else current_block.get('start')

        end_input = input(f"New end time (current: {current_block.get('end')}): ").strip()
        end_time = end_input if end_input else current_block.get('end')

        spacing_input = input(
            f"New spacing (current: {current_block.get('spacing', 60)}): "
        ).strip()

        new_block_data = {
            "start": start_time,
            "end": end_time
        }

        if spacing_input:
            try:
                spacing_value = int(spacing_input)
                if spacing_value <= 0:
                    print("❌ Invalid spacing. Must be greater than 0. Keeping current value.")
                    new_block_data["spacing"] = current_block.get("spacing", 60)
                else:
                    new_block_data["spacing"] = spacing_value
            except ValueError:
                print("❌ Invalid spacing. Keeping current value.")
                new_block_data["spacing"] = current_block.get("spacing", 60)
        else:
            new_block_data["spacing"] = current_block.get("spacing", 60)

        if controller.modify_time_block(day, index, new_block_data):
            print(f"✅ Successfully modified time block for {day}")
        else:
            print("❌ Failed to modify time block.")

    @staticmethod
    def _delete_time_block_interactive(controller: TimeSlotController) -> None:
        """Delete a time block interactively."""
        TimeSlotView._display_time_blocks_only(controller)

        day = input("\nEnter day (MON, TUE, WED, THU, FRI): ").strip().upper()
        if day not in ["MON", "TUE", "WED", "THU", "FRI"]:
            print("❌ Invalid day.")
            return

        time_blocks = controller.get_time_blocks_for_day(day)
        if not time_blocks:
            print(f"❌ No time blocks found for {day}.")
            return

        try:
            index = int(input("Enter time block number to delete: ")) - 1
            if index < 0 or index >= len(time_blocks):
                print("❌ Invalid time block number.")
                return
        except ValueError:
            print("❌ Invalid number.")
            return

        if controller.delete_time_block(day, index):
            print(f"✅ Successfully deleted time block from {day}")
        else:
            print("❌ Failed to delete time block.")

    # Helper methods for class pattern management
    @staticmethod
    def _display_class_patterns_only(controller: TimeSlotController) -> None:
        """Display only class patterns."""
        patterns = controller.get_class_patterns()
        if not patterns:
            print("No class patterns configured.")
            return

        for i, pattern in enumerate(patterns):
            pattern_credits = pattern.get("credits", "N/A")
            disabled = pattern.get("disabled", False)

            # Handle different pattern formats
            if "meetings" in pattern:
                # Config file format with meetings array
                meetings = pattern.get("meetings", [])
                days = [meeting.get("day", "") for meeting in meetings
                       if meeting.get("day")]
                durations = [meeting.get("duration", 0) for meeting in meetings]
                duration = durations[0] if durations else "N/A"
                lab = any(meeting.get("lab", False) for meeting in meetings)
            else:
                # Simple format
                days = pattern.get("days", [])
                duration = pattern.get("duration", "N/A")
                lab = pattern.get("lab", False)

            status = "🔴 Disabled" if disabled else "🟢 Enabled"
            pattern_type = "🔬 Lab" if lab else "📚 Regular"

            print(f"\n   {i + 1}. {pattern_type} Pattern - "
                  f"{pattern_credits} credits ({status})")
            print(f"      Days: {', '.join(days) if days else 'None'}")
            print(f"      Duration: {duration} minutes")

    @staticmethod
    def _add_class_pattern_interactive(controller: TimeSlotController) -> None:
        """Add a class pattern interactively."""
        print("\n🆕 ADD NEW CLASS PATTERN")
        print("=" * 30)

        # Get credits
        try:
            pattern_credits = int(input("Credits (1-6): ").strip())
            if pattern_credits < 1 or pattern_credits > 6:
                print("❌ Credits must be between 1 and 6.")
                return
        except ValueError:
            print("❌ Invalid credits. Must be a number.")
            return

        # Get days
        print("Enter meeting days (e.g., MON,WED,FRI):")
        days_input = input("Days: ").strip().upper()
        days = [day.strip() for day in days_input.split(",") if day.strip()]
        valid_days = {"MON", "TUE", "WED", "THU", "FRI"}

        for day in days:
            if day not in valid_days:
                print(f"❌ Invalid day: {day}. Must be MON, TUE, WED, THU, or FRI.")
                return

        # Get duration
        try:
            duration = int(input("Duration in minutes: ").strip())
            if duration <= 0:
                print("❌ Duration must be positive.")
                return
        except ValueError:
            print("❌ Invalid duration. Must be a number.")
            return

        # Get lab status
        lab_input = input("Is this a lab pattern? (y/n): ").strip().lower()
        is_lab_pattern = lab_input in ["y", "yes"]

        # Create meetings array with proper structure
        meetings = []
        for day in days:
            meeting = {
                "day": day,
                "duration": duration
            }
            if is_lab_pattern:
                meeting["lab"] = True
            meetings.append(meeting)

        # Create pattern data with correct structure
        pattern_data = {
            "credits": pattern_credits,
            "meetings": meetings
        }

        # Add optional fields
        fixed_times_input = input("Fixed start time (optional, e.g., 14:00): ").strip()
        if fixed_times_input:
            pattern_data["start_time"] = fixed_times_input

        disabled_input = input("Disable this pattern? (y/n): ").strip().lower()
        if disabled_input in ["y", "yes"]:
            pattern_data["disabled"] = True

        if controller.add_class_pattern(pattern_data):
            print("✅ Successfully added class pattern")
        else:
            print("❌ Failed to add class pattern.")

    @staticmethod
    def _modify_class_pattern_interactive(controller: TimeSlotController) -> None:
        """Modify a class pattern interactively."""
        TimeSlotView._display_class_patterns_only(controller)

        patterns = controller.get_class_patterns()
        if not patterns:
            print("❌ No class patterns found.")
            return

        try:
            index = int(input("Enter pattern number to modify: ")) - 1
            if index < 0 or index >= len(patterns):
                print("❌ Invalid pattern number.")
                return
        except ValueError:
            print("❌ Invalid number.")
            return

        current_pattern = patterns[index]
        print(f"\nModifying pattern {index + 1}")

        # Extract current values from meetings format
        current_credits = current_pattern.get('credits')
        meetings = current_pattern.get("meetings", [])
        current_days = [meeting.get("day", "") for meeting in meetings]
        current_duration = meetings[0].get("duration", 50) if meetings else 50
        current_lab = any(meeting.get("lab", False) for meeting in meetings)

        print(f"Current: {current_credits} credits, {current_duration} minutes, "
              f"Days: {','.join(current_days)}, Lab: {current_lab}")

        # Get new values with current as defaults
        credits_input = input(f"Credits (current: {current_credits}): ").strip()
        new_credits = int(credits_input) if credits_input else current_credits

        days_input = input(f"Days (current: {','.join(current_days)}): ").strip().upper()
        days = ([day.strip() for day in days_input.split(",") if day.strip()]
               if days_input else current_days)

        duration_input = input(f"Duration (current: {current_duration}): ").strip()
        duration = int(duration_input) if duration_input else current_duration

        lab_input = input(f"Lab pattern? (current: {current_lab}) y/n: ").strip().lower()
        is_lab = lab_input in ["y", "yes"] if lab_input else current_lab

        # Create meetings array with proper structure
        meetings = []
        for day in days:
            meeting = {
                "day": day,
                "duration": duration
            }
            if is_lab:
                meeting["lab"] = True
            meetings.append(meeting)

        # Create pattern with correct structure
        new_pattern = {
            "credits": new_credits,
            "meetings": meetings
        }

        # Preserve optional fields
        if "start_time" in current_pattern:
            new_pattern["start_time"] = current_pattern["start_time"]
        if "disabled" in current_pattern:
            new_pattern["disabled"] = current_pattern["disabled"]

        if controller.modify_class_pattern(index, new_pattern):
            print("✅ Successfully modified class pattern")
        else:
            print("❌ Failed to modify class pattern.")

    @staticmethod
    def _delete_class_pattern_interactive(controller: TimeSlotController) -> None:
        """Delete a class pattern interactively."""
        TimeSlotView._display_class_patterns_only(controller)

        patterns = controller.get_class_patterns()
        if not patterns:
            print("❌ No class patterns found.")
            return

        try:
            index = int(input("Enter pattern number to delete: ")) - 1
            if index < 0 or index >= len(patterns):
                print("❌ Invalid pattern number.")
                return
        except ValueError:
            print("❌ Invalid number.")
            return

        if controller.delete_class_pattern(index):
            print("✅ Successfully deleted class pattern")
        else:
            print("❌ Failed to delete class pattern.")

    @staticmethod
    def _toggle_pattern_status_interactive(controller: TimeSlotController) -> None:
        """Toggle pattern enabled/disabled status."""
        TimeSlotView._display_class_patterns_only(controller)

        patterns = controller.get_class_patterns()
        if not patterns:
            print("❌ No class patterns found.")
            return

        try:
            index = int(input("Enter pattern number to toggle: ")) - 1
            if index < 0 or index >= len(patterns):
                print("❌ Invalid pattern number.")
                return
        except ValueError:
            print("❌ Invalid number.")
            return

        if controller.toggle_pattern_status(index):
            current_status = patterns[index].get("disabled", False)
            new_status = "Disabled" if not current_status else "Enabled"  # Status after toggle
            print(f"✅ Pattern is now {new_status}")
        else:
            print("❌ Failed to toggle pattern status.")
