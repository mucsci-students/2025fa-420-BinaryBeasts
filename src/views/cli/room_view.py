# src/views/cli/room_view.py


class RoomView:
    """View layer for room management - handles all user interaction and display."""

    @staticmethod
    def display_rooms(controller) -> None:
        """Display all rooms in a formatted list."""
        print("\n" + "=" * 60)
        print("ROOM LIST")
        print("=" * 60)

        rooms = controller.get_rooms()
        if not rooms:
            print("No rooms found.")
            return

        print(f"📍 Total Rooms: {len(rooms)}")
        print("-" * 60)

        for i, room in enumerate(rooms, 1):
            print(f"{i:3}. 🏢 {room}")

        print("=" * 60)

    @staticmethod
    def add_room_interactive(controller) -> None:
        """Interactive room addition."""
        print("\n🆕 ADD NEW ROOM")
        print("=" * 30)

        room_name = input("Room name (e.g., Roddy 101): ").strip()
        if not room_name:
            print("❌ Room name cannot be empty.")
            return

        try:
            if controller.add_room(room_name):
                print(f"✅ Successfully added room: {room_name}")
            else:
                print(f"❌ Room '{room_name}' already exists.")
        except Exception as e:
            print(f"❌ Error adding room: {e}")

    @staticmethod
    def modify_room_interactive(controller) -> None:
        """Interactive room editing/renaming."""
        RoomView.display_rooms(controller)

        rooms = controller.get_rooms()
        if not rooms:
            print("❌ No rooms available to edit.")
            return

        old_name = input("\nEnter current room name to edit: ").strip()
        if not old_name:
            print("❌ Room name cannot be empty.")
            return

        if old_name not in rooms:
            print(f"❌ Room '{old_name}' not found.")
            return

        new_name = input(f"Enter new name for '{old_name}': ").strip()
        if not new_name:
            print("❌ New room name cannot be empty.")
            return

        try:
            if controller.edit_room(old_name, new_name):
                print(f"✅ Successfully renamed '{old_name}' to '{new_name}'")
                print(
                    "📝 Note: All course and faculty references have been updated automatically."
                )
            else:
                if new_name in rooms:
                    print(f"❌ Room '{new_name}' already exists.")
                else:
                    print(f"❌ Failed to rename room.")
        except Exception as e:
            print(f"❌ Error editing room: {e}")

    @staticmethod
    def delete_room_interactive(controller, courses_list, faculty_list) -> None:
        """Interactive room deletion with impact analysis."""
        RoomView.display_rooms(controller)

        rooms = controller.get_rooms()
        if not rooms:
            print("❌ No rooms available to delete.")
            return

        room_name = input("\nEnter room name to delete: ").strip()
        if not room_name:
            print("❌ Room name cannot be empty.")
            return

        if room_name not in rooms:
            print(f"❌ Room '{room_name}' not found.")
            return

        # Analyze impact of deletion
        print(f"\n🔍 ANALYZING IMPACT OF DELETING '{room_name}':")
        print("-" * 50)

        # Check courses using this room
        affected_courses = []
        for course_id, instances in courses_list.items():
            for course in instances:
                if room_name in course.room:
                    affected_courses.append(course_id)
                    break  # Only count course once

        # Check faculty preferences
        affected_faculty = []
        for name, faculty in faculty_list.items():
            if room_name in faculty.room_preferences:
                affected_faculty.append(name)

        if affected_courses:
            print(f"📚 Courses using this room ({len(affected_courses)}):")
            for course in affected_courses:
                print(f"   • {course}")

        if affected_faculty:
            print(
                f"👥 Faculty with preferences for this room ({len(affected_faculty)}):"
            )
            for faculty in affected_faculty:
                print(f"   • {faculty}")

        if not affected_courses and not affected_faculty:
            print("✅ No conflicts found. Room can be safely deleted.")
        else:
            print("\n⚠️  Warning: Deleting this room will:")
            if affected_courses:
                print(
                    f"   • Remove room assignment from {len(affected_courses)} course(s)"
                )
            if affected_faculty:
                print(
                    f"   • Remove room preferences from {len(affected_faculty)} faculty member(s)"
                )

        # Confirm deletion
        confirm = (
            input(f"\nAre you sure you want to delete '{room_name}'? (y/N): ")
            .strip()
            .lower()
        )
        if confirm in ["y", "yes"]:
            try:
                if controller.delete_room(room_name):
                    print(f"✅ Successfully deleted room: {room_name}")
                    if affected_courses or affected_faculty:
                        print(
                            "📝 Note: References should be manually updated if needed."
                        )
                else:
                    print(f"❌ Failed to delete room '{room_name}'.")
            except Exception as e:
                print(f"❌ Error deleting room: {e}")
        else:
            print("Deletion cancelled.")

    @staticmethod
    def show_menu() -> None:
        """Display the main menu."""
        print("\n" + "=" * 50)
        print("ROOM MANAGEMENT")
        print("=" * 50)
        print("1. 👀 View all rooms")
        print("2. ➕ Add new room")
        print("3. ✏️ Modify existing room")
        print("4. ❌ Delete room")
        print("5. 💾 Save changes and exit")
        print("6. 🚪 Exit without saving")
        print("=" * 50)

    @staticmethod
    def get_menu_choice() -> str:
        """Get user's menu choice."""
        return input("Select an option (1-6): ").strip()
