# src/views/cli/lab_view_cli.py


class LabView:
    """View layer for lab management - handles all user interaction and display."""

    @staticmethod
    def display_labs(controller) -> None:
        """Display all labs in a formatted list."""
        print("\n" + "=" * 60)
        print("LAB LIST")
        print("=" * 60)

        labs = controller.get_labs()
        if not labs:
            print("No labs found.")
            return

        print(f"🔬 Total Labs: {len(labs)}")
        print("-" * 60)

        for i, lab in enumerate(labs, 1):
            print(f"{i:3}. 🧪 {lab}")

        print("=" * 60)

    @staticmethod
    def add_lab_interactive(controller) -> None:
        """Interactive lab addition."""
        print("\n🆕 ADD NEW LAB")
        print("=" * 30)

        lab_name = input("Lab name (e.g., Mac, Linux, Windows): ").strip()
        if not lab_name:
            print("❌ Lab name cannot be empty.")
            return

        try:
            if controller.add_lab(lab_name):
                print(f"✅ Successfully added lab: {lab_name}")
            else:
                print(f"❌ Lab '{lab_name}' already exists.")
        except Exception as e:
            print(f"❌ Error adding lab: {e}")

    @staticmethod
    def modify_lab_interactive(controller) -> None:
        """Interactive lab editing/renaming."""
        LabView.display_labs(controller)

        labs = controller.get_labs()
        if not labs:
            print("❌ No labs available to edit.")
            return

        old_name = input("\nEnter current lab name to edit: ").strip()
        if not old_name:
            print("❌ Lab name cannot be empty.")
            return

        if old_name not in labs:
            print(f"❌ Lab '{old_name}' not found.")
            return

        new_name = input(f"Enter new name for '{old_name}': ").strip()
        if not new_name:
            print("❌ New lab name cannot be empty.")
            return

        try:
            if controller.edit_lab(old_name, new_name):
                print(f"✅ Successfully renamed '{old_name}' to '{new_name}'")
                print(
                    "📝 Note: All course and faculty references have been updated automatically."
                )
            else:
                if new_name in labs:
                    print(f"❌ Lab '{new_name}' already exists.")
                else:
                    print(f"❌ Failed to rename lab.")
        except Exception as e:
            print(f"❌ Error editing lab: {e}")

    @staticmethod
    def delete_lab_interactive(controller, courses_list, faculty_list) -> None:
        """Interactive lab deletion with impact analysis."""
        LabView.display_labs(controller)

        labs = controller.get_labs()
        if not labs:
            print("❌ No labs available to delete.")
            return

        lab_name = input("\nEnter lab name to delete: ").strip()
        if not lab_name:
            print("❌ Lab name cannot be empty.")
            return

        if lab_name not in labs:
            print(f"❌ Lab '{lab_name}' not found.")
            return

        # Analyze impact of deletion
        print(f"\n🔍 ANALYZING IMPACT OF DELETING '{lab_name}':")
        print("-" * 50)

        # Check courses using this lab
        affected_courses = []
        for course_id, instances in courses_list.items():
            for course in instances:
                if lab_name in course.lab:
                    affected_courses.append(course_id)
                    break  # Only count course once

        # Check faculty preferences
        affected_faculty = []
        for name, faculty in faculty_list.items():
            if lab_name in faculty.lab_preferences:
                affected_faculty.append(name)

        if affected_courses:
            print(f"📚 Courses using this lab ({len(affected_courses)}):")
            for course in affected_courses:
                print(f"   • {course}")

        if affected_faculty:
            print(
                f"👥 Faculty with preferences for this lab ({len(affected_faculty)}):"
            )
            for faculty in affected_faculty:
                print(f"   • {faculty}")

        if not affected_courses and not affected_faculty:
            print("✅ No conflicts found. Lab can be safely deleted.")
        else:
            print("\n⚠️  Warning: Deleting this lab will:")
            if affected_courses:
                print(
                    f"   • Remove lab assignment from {len(affected_courses)} course(s)"
                )
            if affected_faculty:
                print(
                    f"   • Remove lab preferences from {len(affected_faculty)} faculty member(s)"
                )

        # Confirm deletion
        confirm = (
            input(f"\nAre you sure you want to delete '{lab_name}'? (y/N): ")
            .strip()
            .lower()
        )
        if confirm in ["y", "yes"]:
            try:
                if controller.delete_lab(lab_name):
                    print(f"✅ Successfully deleted lab: {lab_name}")
                    if affected_courses or affected_faculty:
                        print(
                            "📝 Note: References should be manually updated if needed."
                        )
                else:
                    print(f"❌ Failed to delete lab '{lab_name}'.")
            except Exception as e:
                print(f"❌ Error deleting lab: {e}")
        else:
            print("Deletion cancelled.")

    @staticmethod
    def show_menu() -> None:
        """Display the main menu."""
        print("\n" + "=" * 50)
        print("LAB MANAGEMENT")
        print("=" * 50)
        print("1. 👀 View all labs")
        print("2. ➕ Add new lab")
        print("3. ✏️ Modify existing lab")
        print("4. ❌ Delete lab")
        print("5. 💾 Save changes and exit")
        print("6. 🚪 Exit without saving")
        print("=" * 50)

    @staticmethod
    def get_menu_choice() -> str:
        """Get user's menu choice."""
        return input("Select an option (1-6): ").strip()
