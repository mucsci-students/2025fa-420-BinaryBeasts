# src/views/cli/course_view_cli.py
from src.controllers.course_controller import CourseController


class CourseView:
    @staticmethod
    def display_courses(controller: CourseController) -> None:
        print("\n" + "=" * 60)
        print("COURSE LIST")
        print("=" * 60)

        all_courses = controller.list_courses()
        if not all_courses:
            print("No courses found.")
            return

        for course_id, instances in all_courses.items():
            print(f"\n📖 {course_id}")
            for i, course in enumerate(instances):
                instance_label = f" (Instance {i + 1})" if len(instances) > 1 else ""
                print(f"   {instance_label}")
                print(f"   📊 Credits: {course.credits}")
                print(
                    f"   🏢 Rooms: {', '.join(course.room) if course.room else 'None'}"
                )
                print(f"   🔬 Labs: {', '.join(course.lab) if course.lab else 'None'}")
                print(
                    f"   👤 Faculty: {', '.join(course.faculty) if course.faculty else 'Unassigned'}"
                )
                print(
                    f"   ⚠️  Conflicts: {', '.join(course.conflicts) if course.conflicts else 'None'}"
                )
                if i < len(instances) - 1:
                    print("   " + "-" * 40)
        print("=" * 60)

    @staticmethod
    def get_course_input() -> dict:
        """Get course information from user input."""

        print("\n🆕 ADD NEW COURSE")
        print("=" * 30)

        course_id = input("Course ID (e.g., CMSC 101): ").strip()
        if not course_id:
            raise ValueError("Course ID cannot be empty")

        while True:
            try:
                credits = int(input("Credits (1-6): ").strip())
                if credits < 1 or credits > 6:
                    print("Error: Credits must be between 1 and 6")
                    continue
                break
            except ValueError:
                print("Error: Please enter a valid number for credits")

        print("\nRooms (press Enter to finish):")
        rooms = []
        while True:
            room = input(f"  Room {len(rooms) + 1} (or Enter to finish): ").strip()
            if not room:
                break
            rooms.append(room)

        print("\nLabs (press Enter to finish):")
        labs = []
        while True:
            lab = input(f"  Lab {len(labs) + 1} (or Enter to finish): ").strip()
            if not lab:
                break
            labs.append(lab)

        print("\nFaculty (press Enter to finish):")
        faculty = []
        while True:
            fac = input(f"  Faculty {len(faculty) + 1} (or Enter to finish): ").strip()
            if not fac:
                break
            faculty.append(fac)

        print("\nConflicting courses (press Enter to finish):")
        conflicts = []
        while True:
            conflict = input(
                f"  Conflict {len(conflicts) + 1} (or Enter to finish): "
            ).strip()
            if not conflict:
                break
            conflicts.append(conflict)

        return {
            "course_id": course_id,
            "credits": credits,
            "room": rooms,
            "lab": labs,
            "faculty": faculty,
            "conflicts": conflicts,
        }

    @staticmethod
    def add_course_interactive(controller: CourseController) -> None:
        try:
            data = CourseView.get_course_input()
            controller.add_course(data)
            print(f"✅ Successfully added course: {data['course_id']}")
        except Exception as e:
            print(f"❌ Error adding course: {e}")

    @staticmethod
    def modify_course_interactive(controller: CourseController) -> None:
        CourseView.display_courses(controller)
        course_id = input("\nEnter Course ID to modify: ").strip()
        course_instances = controller.get_course(course_id)

        if not course_instances:
            print(f"❌ Course {course_id} not found.")
            return

        if len(course_instances) > 1:
            print(f"\nFound {len(course_instances)} instances of {course_id}:")
            for i, _ in enumerate(course_instances):
                print(f"  {i + 1}. Instance {i + 1}")
            while True:
                try:
                    choice = int(input("Select instance to modify (number): ")) - 1
                    if 0 <= choice < len(course_instances):
                        break
                    print("Invalid choice. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")
        else:
            choice = 0

        current_course = course_instances[choice]
        print(f"\n📝 MODIFYING: {current_course.course_id} (Section {choice + 1})")

        # Get new values, showing current values as defaults
        print(f"\nCurrent credits: {current_course.credits}")
        credits_input = input("New credits (press Enter to keep current): ").strip()
        credits = int(credits_input) if credits_input else current_course.credits

        print(
            f"\nCurrent rooms: {', '.join(current_course.room) if current_course.room else 'None'}"
        )
        print("Enter new rooms (press Enter to finish, 'keep' to keep current):")
        rooms_input = input("  New rooms (or 'keep'): ").strip().lower()
        if rooms_input == "keep":
            rooms = current_course.room
        else:
            rooms = []
            if rooms_input:
                rooms.append(rooms_input)
            while True:
                room = input(f"  Room {len(rooms) + 1} (or Enter to finish): ").strip()
                if not room:
                    break
                rooms.append(room)

        # Similar for other fields
        print(
            f"\nCurrent labs: {', '.join(current_course.lab) if current_course.lab else 'None'}"
        )
        labs_input = (
            input("Enter new labs ('keep' to keep current, Enter for none): ")
            .strip()
            .lower()
        )
        if labs_input == "keep":
            labs = current_course.lab
        else:
            labs = []
            if labs_input and labs_input != "keep":
                labs.append(labs_input)
                while True:
                    lab = input(f"  Lab {len(labs) + 1} (or Enter to finish): ").strip()
                    if not lab:
                        break
                    labs.append(lab)

        print(
            f"\nCurrent faculty: {', '.join(current_course.faculty) if current_course.faculty else 'None'}"
        )
        faculty_input = (
            input("Enter new faculty ('keep' to keep current, Enter for none): ")
            .strip()
            .lower()
        )
        if faculty_input == "keep":
            faculty = current_course.faculty
        else:
            faculty = []
            if faculty_input and faculty_input != "keep":
                faculty.append(faculty_input)
                while True:
                    fac = input(
                        f"  Faculty {len(faculty) + 1} (or Enter to finish): "
                    ).strip()
                    if not fac:
                        break
                    faculty.append(fac)

        print(
            f"\nCurrent conflicts: {', '.join(current_course.conflicts) if current_course.conflicts else 'None'}"
        )
        conflicts_input = (
            input("Enter new conflicts ('keep' to keep current, Enter for none): ")
            .strip()
            .lower()
        )
        if conflicts_input == "keep":
            conflicts = current_course.conflicts
        else:
            conflicts = []
            if conflicts_input and conflicts_input != "keep":
                conflicts.append(conflicts_input)
                while True:
                    conflict = input(
                        f"  Conflict {len(conflicts) + 1} (or Enter to finish): "
                    ).strip()
                    if not conflict:
                        break
                    conflicts.append(conflict)
        # Delete old course and add modified version
        controller.delete_course(course_id, choice)
        new_course_data = {
            "course_id": current_course.course_id,
            "credits": credits,
            "room": rooms,
            "lab": labs,
            "faculty": faculty,
            "conflicts": conflicts,
        }
        controller.add_course(new_course_data)

        print(f"✅ Successfully modified course: {current_course.course_id}")

    @staticmethod
    def delete_course_interactive(controller: CourseController) -> None:
        CourseView.display_courses(controller)
        course_id = input("\nEnter Course ID to delete: ").strip()
        course_instances = controller.get_course(course_id)

        if not course_instances:
            print(f"❌ Course {course_id} not found.")
            return

        if len(course_instances) > 1:
            print(f"\nFound {len(course_instances)} instances of {course_id}:")
            print("  0. Delete ALL instances")
            for i, _ in enumerate(course_instances):
                print(f"  {i + 1}. Delete instance {i + 1}")

            while True:
                try:
                    choice = int(input("Select option (number): "))
                    if 0 <= choice <= len(course_instances):
                        break
                    print("Invalid choice. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")

            if choice == 0:
                # Delete all
                for _ in range(len(course_instances)):
                    controller.delete_course(course_id, 0)
                print(f"✅ Successfully deleted all instances of course: {course_id}")
            else:
                controller.delete_course(course_id, choice - 1)
                print(
                    f"✅ Successfully deleted instance {choice} of course: {course_id}"
                )
        else:
            confirm = (
                input(f"Are you sure you want to delete {course_id}? (y/N): ")
                .strip()
                .lower()
            )
            if confirm in ["y", "yes"]:
                controller.delete_course(course_id, 0)
                print(f"✅ Successfully deleted course: {course_id}")
            else:
                print("Deletion cancelled.")

    @staticmethod
    def show_menu() -> None:
        """Display the main menu."""
        print("\n" + "=" * 50)
        print("COURSE MANAGEMENT")
        print("=" * 50)
        print("1. 👀 View all courses")
        print("2. ➕ Add new course")
        print("3. ✏️ Modify existing course")
        print("4. ❌ Delete course")
        print("5. 💾 Save changes and exit")
        print("6. 🚪 Exit without saving")
        print("7. ↩️ Undo last change")
        print("8. ↪️ Redo last change")
        print("=" * 50)

    @staticmethod
    def get_menu_choice() -> str:
        """Get user's menu choice."""
        return input("Select an option (1-8): ").strip()
