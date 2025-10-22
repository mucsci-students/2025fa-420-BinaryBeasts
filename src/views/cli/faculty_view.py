# src/views/cli/faculty_view.py


class FacultyView:
    """View layer for faculty management - handles all user interaction and display."""

    @staticmethod
    def display_faculty(controller) -> None:
        """Display all faculty members in a formatted list."""
        print("\n" + "=" * 60)
        print("FACULTY LIST")
        print("=" * 60)

        faculty_dict = controller.list_faculty()
        if not faculty_dict:
            print("No faculty found.")
            return

        print(f"👥 Total Faculty: {len(faculty_dict)}")
        print("-" * 60)

        for i, (name, faculty) in enumerate(faculty_dict.items(), 1):
            print(f"\n{i:3}. 👤 {name}")
            print(
                f"      📊 Credit range: {faculty.minimum_credits}-{faculty.maximum_credits}"
            )
            print(f"      📚 Max unique courses: {faculty.unique_course_limit}")

            # Show availability
            times = faculty.times
            available_days = [day for day, slots in times.items() if slots]
            print(f"      📅 Available days: {', '.join(available_days) or 'None'}")

            # Show course preferences
            course_prefs = faculty.course_preferences
            if course_prefs:
                top_courses = sorted(
                    course_prefs.items(), key=lambda x: x[1], reverse=True
                )[:3]
                print(
                    f"      ⭐ Preferred courses: {', '.join([f'{c}({p})' for c, p in top_courses])}"
                )
            else:
                print("      ⭐ Preferred courses: None")

            # Show room preferences
            room_prefs = faculty.room_preferences
            if room_prefs:
                top_rooms = sorted(
                    room_prefs.items(), key=lambda x: x[1], reverse=True
                )[:3]
                print(
                    f"      🏢 Preferred rooms: {', '.join([f'{r}({p})' for r, p in top_rooms])}"
                )
            else:
                print("      🏢 Preferred rooms: None")

            # Show lab preferences
            lab_prefs = faculty.lab_preferences
            if lab_prefs:
                top_labs = sorted(lab_prefs.items(), key=lambda x: x[1], reverse=True)[
                    :3
                ]
                print(
                    f"      🔬 Preferred labs: {', '.join([f'{l}({p})' for l, p in top_labs])}"
                )
            else:
                print("      🔬 Preferred labs: None")

        print("=" * 60)

    @staticmethod
    def get_faculty_input(available_courses, available_rooms, available_labs) -> dict:
        """Get faculty information from user input."""
        print("\n🆕 ADD NEW FACULTY")
        print("=" * 30)

        name = input("Faculty name (e.g., Dr. Smith): ").strip()
        if not name:
            raise ValueError("Faculty name cannot be empty")

        # Get credit limits
        while True:
            try:
                min_credits = int(input("Minimum credits (0-20): ").strip())
                if min_credits < 0 or min_credits > 20:
                    print("Error: Minimum credits must be between 0 and 20")
                    continue
                break
            except ValueError:
                print("Error: Please enter a valid number for minimum credits")

        while True:
            try:
                max_credits = int(input("Maximum credits (0-20): ").strip())
                if max_credits < min_credits or max_credits > 20:
                    print(
                        f"Error: Maximum credits must be between {min_credits} and 20"
                    )
                    continue
                break
            except ValueError:
                print("Error: Please enter a valid number for maximum credits")

        while True:
            try:
                unique_limit = int(input("Unique course limit (1-10): ").strip())
                if unique_limit < 1 or unique_limit > 10:
                    print("Error: Unique course limit must be between 1 and 10")
                    continue
                break
            except ValueError:
                print("Error: Please enter a valid number for unique course limit")

        # Get availability times
        print("\nAvailability times (format: HH:MM-HH:MM, press Enter to skip day):")
        times = {}
        days = ["MON", "TUE", "WED", "THU", "FRI"]
        for day in days:
            time_input = input(f"  {day} (e.g., 09:00-17:00): ").strip()
            if time_input:
                times[day] = [time_input]
            else:
                times[day] = []

        # Get course preferences
        print(
            f"\nCourse preferences (available courses: {', '.join(sorted(available_courses))})"
        )
        print("Format: CourseID:preference (0-10), press Enter to finish:")
        course_preferences = {}
        while True:
            pref_input = input(
                f"  Course preference {len(course_preferences) + 1} (or Enter to finish): "
            ).strip()
            if not pref_input:
                break
            try:
                course_id, pref_str = pref_input.split(":")
                course_id = course_id.strip()
                preference = int(pref_str.strip())
                if preference < 0 or preference > 10:
                    print("Error: Preference must be between 0 and 10")
                    continue
                if course_id in available_courses:
                    course_preferences[course_id] = preference
                else:
                    print(
                        f"Warning: Course '{course_id}' not found in available courses"
                    )
            except ValueError:
                print("Error: Format should be CourseID:preference (e.g., CMSC140:8)")

        # Get room preferences
        print(f"\nRoom preferences (available rooms: {', '.join(available_rooms)})")
        print("Format: RoomName:preference (0-10), press Enter to finish:")
        room_preferences = {}
        while True:
            pref_input = input(
                f"  Room preference {len(room_preferences) + 1} (or Enter to finish): "
            ).strip()
            if not pref_input:
                break
            try:
                room_name, pref_str = pref_input.split(":")
                room_name = room_name.strip()
                preference = int(pref_str.strip())
                if preference < 0 or preference > 10:
                    print("Error: Preference must be between 0 and 10")
                    continue
                if room_name in available_rooms:
                    room_preferences[room_name] = preference
                else:
                    print(f"Warning: Room '{room_name}' not found in available rooms")
            except ValueError:
                print("Error: Format should be RoomName:preference (e.g., Roddy136:8)")

        # Get lab preferences
        print(f"\nLab preferences (available labs: {', '.join(available_labs)})")
        print("Format: LabName:preference (0-10), press Enter to finish:")
        lab_preferences = {}
        while True:
            pref_input = input(
                f"  Lab preference {len(lab_preferences) + 1} (or Enter to finish): "
            ).strip()
            if not pref_input:
                break
            try:
                lab_name, pref_str = pref_input.split(":")
                lab_name = lab_name.strip()
                preference = int(pref_str.strip())
                if preference < 0 or preference > 10:
                    print("Error: Preference must be between 0 and 10")
                    continue
                if lab_name in available_labs:
                    lab_preferences[lab_name] = preference
                else:
                    print(f"Warning: Lab '{lab_name}' not found in available labs")
            except ValueError:
                print("Error: Format should be LabName:preference (e.g., Linux:8)")

        return {
            "name": name,
            "minimum_credits": min_credits,
            "maximum_credits": max_credits,
            "unique_course_limit": unique_limit,
            "times": times,
            "course_preferences": course_preferences,
            "room_preferences": room_preferences,
            "lab_preferences": lab_preferences,
        }

    @staticmethod
    def add_faculty_interactive(
        controller, available_courses, available_rooms, available_labs
    ) -> None:
        """Interactive faculty addition."""
        try:
            faculty_data = FacultyView.get_faculty_input(
                available_courses, available_rooms, available_labs
            )
            if controller.add_faculty(faculty_data):
                print(f"✅ Successfully added faculty: {faculty_data['name']}")
            else:
                print(f"❌ Faculty '{faculty_data['name']}' already exists.")
        except Exception as e:
            print(f"❌ Error adding faculty: {e}")

    @staticmethod
    def modify_faculty_interactive(
        controller, available_courses, available_rooms, available_labs
    ) -> None:
        """Interactive faculty editing."""
        FacultyView.display_faculty(controller)

        faculty_dict = controller.list_faculty()
        if not faculty_dict:
            print("❌ No faculty available to edit.")
            return

        name = input("\nEnter faculty name to modify: ").strip()
        if not name:
            print("❌ Faculty name cannot be empty.")
            return

        # Check if faculty exists
        if not controller.faculty_exists(name):
            print(f"❌ Faculty '{name}' not found.")
            return

        print(f"\n📝 MODIFYING: {name}")
        print("Enter new values (press Enter to keep current value):")

        # Get current faculty data
        current_faculty = controller.get_faculty(name)

        # Get new name (optional)
        new_name = input(f"New name (current: {name}): ").strip()
        if not new_name:
            new_name = name

        # Get new credit limits (optional)
        min_credits_input = input(
            f"New minimum credits (current: {current_faculty.minimum_credits}): "
        ).strip()
        min_credits = (
            int(min_credits_input)
            if min_credits_input
            else current_faculty.minimum_credits
        )

        max_credits_input = input(
            f"New maximum credits (current: {current_faculty.maximum_credits}): "
        ).strip()
        max_credits = (
            int(max_credits_input)
            if max_credits_input
            else current_faculty.maximum_credits
        )

        unique_limit_input = input(
            f"New unique course limit (current: {current_faculty.unique_course_limit}): "
        ).strip()
        unique_limit = (
            int(unique_limit_input)
            if unique_limit_input
            else current_faculty.unique_course_limit
        )

        # Ask if they want to update preferences
        update_prefs = (
            input("Update preferences and times? (y/n, default: n): ").strip().lower()
        )
        if update_prefs in ["y", "yes"]:
            print(
                "Note: Complete faculty preference update - enter all preferences you want to keep:"
            )
            try:
                faculty_input = FacultyView.get_faculty_input(
                    available_courses, available_rooms, available_labs
                )
                new_data = {
                    "name": new_name,
                    "minimum_credits": min_credits,
                    "maximum_credits": max_credits,
                    "unique_course_limit": unique_limit,
                    "times": faculty_input["times"],
                    "course_preferences": faculty_input["course_preferences"],
                    "room_preferences": faculty_input["room_preferences"],
                    "lab_preferences": faculty_input["lab_preferences"],
                }
            except Exception as e:
                print(f"❌ Error getting preferences: {e}")
                return
        else:
            # Keep existing preferences
            new_data = {
                "name": new_name,
                "minimum_credits": min_credits,
                "maximum_credits": max_credits,
                "unique_course_limit": unique_limit,
                "times": current_faculty.times,
                "course_preferences": current_faculty.course_preferences,
                "room_preferences": current_faculty.room_preferences,
                "lab_preferences": current_faculty.lab_preferences,
            }

        try:
            if controller.modify_faculty(name, new_data):
                print(f"✅ Successfully modified faculty: {name}")
                if new_name != name:
                    print(f"📝 Note: Faculty renamed from '{name}' to '{new_name}'")
            else:
                print("❌ Failed to modify faculty. Name may already exist.")
        except Exception as e:
            print(f"❌ Error modifying faculty: {e}")

    @staticmethod
    def delete_faculty_interactive(controller, courses_list) -> None:
        """Interactive faculty deletion with impact analysis."""
        FacultyView.display_faculty(controller)

        faculty_dict = controller.list_faculty()
        if not faculty_dict:
            print("❌ No faculty available to delete.")
            return

        name = input("\nEnter faculty name to delete: ").strip()
        if not name:
            print("❌ Faculty name cannot be empty.")
            return

        # Check if faculty exists
        if not controller.faculty_exists(name):
            print(f"❌ Faculty '{name}' not found.")
            return

        # Analyze impact of deletion
        print(f"\n🔍 ANALYZING IMPACT OF DELETING '{name}':")
        print("-" * 50)

        # Check courses assigned to this faculty
        affected_courses = []
        for course_id, instances in courses_list.items():
            for course in instances:
                if name in course.faculty:
                    affected_courses.append(course_id)
                    break  # Only count course once

        if affected_courses:
            print(f"📚 Courses assigned to this faculty ({len(affected_courses)}):")
            for course in affected_courses:
                print(f"   • {course}")
        else:
            print("✅ No courses currently assigned to this faculty.")

        if affected_courses:
            print("\n⚠️  Warning: Deleting this faculty member will:")
            print(
                f"   • Remove faculty assignment from {len(affected_courses)} course(s)"
            )

        # Confirm deletion
        confirm = (
            input(f"\nAre you sure you want to delete faculty '{name}'? (y/N): ")
            .strip()
            .lower()
        )
        if confirm in ["y", "yes"]:
            try:
                if controller.delete_faculty(name):
                    print(f"✅ Successfully deleted faculty: {name}")
                    if affected_courses:
                        print(
                            "📝 Note: Course references should be manually updated if needed."
                        )
                else:
                    print(f"❌ Failed to delete faculty '{name}'.")
            except Exception as e:
                print(f"❌ Error deleting faculty: {e}")
        else:
            print("Deletion cancelled.")

    @staticmethod
    def show_menu() -> None:
        """Display the main menu."""
        print("\n" + "=" * 50)
        print("FACULTY MANAGEMENT")
        print("=" * 50)
        print("1. 👀 View all faculty")
        print("2. ➕ Add new faculty")
        print("3. ✏️ Modify existing faculty")
        print("4. ❌ Delete faculty")
        print("5. 💾 Save changes and exit")
        print("6. 🚪 Exit without saving")
        print("=" * 50)

    @staticmethod
    def get_menu_choice() -> str:
        """Get user's menu choice."""
        return input("Select an option (1-6): ").strip()
