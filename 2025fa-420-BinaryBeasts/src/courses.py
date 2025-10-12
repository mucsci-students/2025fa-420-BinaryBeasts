# comment

from typing import Dict, List, Set, Optional

class Course:
    """
    Represents an individual course.
    """

    def __init__(self, course_id: str, credits: int,
                 room: List[str] = None,
                 lab: List[str] = None,
                 conflicts: List[str] = None,
                 faculty: List[str] = None):
        # Required fields
        self.course_id = course_id
        self.credits = credits

        self.room = room if room is not None else []
        self.lab = lab if lab is not None else []
        self.conflicts = conflicts if conflicts is not None else []
        self.faculty = faculty if faculty is not None else []

        # Validation
        if not self.course_id:
            raise ValueError("Course ID cannot be empty")
        if self.credits <= 0:
            raise ValueError("Credits must be positive")


class CourseManager:

    def __init__(self, schedule: Optional[Dict[str, List[Course]]] = None) -> None:
        self.courses: Dict[str, List[Course]] = schedule or {}
        self.rooms: Set[str] = set()
        self.labs: Set[str] = set()
        self.faculty: Set[str] = set()
        self.conflict_manager = None
        self.get_resources()

    def load_courses(self, courses_data: List[Dict]) -> None:
        """
        Load the course data from JSON files.
        """
        for cd in courses_data:
            try:
                course = Course(
                    course_id=str(cd.get("course_id", "")).strip(),
                    credits=int(cd.get("credits", 0)),
                    room=list(cd.get("room", [])),
                    lab=list(cd.get("lab", [])),
                    conflicts=list(cd.get("conflicts", [])),
                    faculty=list(cd.get("faculty", [])),
                )
                self.add_course(course)
            except (ValueError, TypeError) as e:
                print(f"warning invalid course data {e}")

    def add_course(self, course: Course) -> None:
        """
        Add a course to the database.

        Creates a new list for course_id if not present.
        Appends this course instance to the list for its course_id.
        Updates resource sets (rooms, labs, faculty).
        :param course: Course object to add
        """
        if course.course_id not in self.courses:
            self.courses[course.course_id] = []
        self.courses[course.course_id].append(course)
        # Update with this course's data.
        self.rooms.update(course.room)
        self.labs.update(course.lab)
        self.faculty.update(course.faculty)

    def delete_course(self, course_id: str, index: int) -> bool:
        """
        Delete the specified course from the schedule.

        Removes the course at (course_id, index).
        If list becomes empty, removes the course_id key.
        Rebuilds resource sets after deletion.

        :param course_id: Course ID to delete
        :param index: Course index to delete
        :return: True if deleted, False if not

        """
        if course_id not in self.courses:
            return False
        if 0 <= index < len(self.courses[course_id]):
            self.courses[course_id].pop(index) # remove the instance
            if not self.courses[course_id]:
                del self.courses[course_id]
        self.get_resources() # refresh resources to remove old values
        return True

    def get_resources(self) -> None:
        """
        Clears rooms, labs, and faculty.
        Iterates over all courses and collects unique values.

        """
        self.rooms.clear()
        self.labs.clear()
        self.faculty.clear()

        for instances in self.courses.values():
            for course in instances:
                self.rooms.update(course.room)
                self.labs.update(course.lab)
                self.faculty.update(course.faculty)

    def get_course_ids(self) -> List[str]:
        """
        Get all course IDs.
        :return: list of course_id strings
        """
        return list(self.courses.keys())

    def get_course(self, course_id: str) -> List[Course]:
        """
        Get all instances of a course.

        Returns a new list wrapper around the stored instances.

        :param course_id: course identifier
        :return: list of Course objects

        """
        return list(self.courses.get(course_id, []))

    def get_all_courses(self) -> Dict[str, List[Course]]:
        """
        Get all courses.
        """
        return self.courses.copy()


    def modify_course(self, course_id: str, index: int, new_course:Course) -> bool:
        """
        Modify the specified course in the schedule.
        """
        if course_id not in self.courses or not (0 <= index < len(self.courses[course_id])):
            return False
        if new_course.credits <= 0:
            raise ValueError("Credits must be positive")

        self.courses[course_id][index] = new_course
        self.get_resources()
        return True

    def course_exists(self, course_id: str) -> bool:
        """
        Check if a course exists.

        :param course_id: course identifier
        :return: True if found, False otherwise
        """
        return course_id in self.courses


    def get_conflicting_courses(self, course_id: str) -> Set[str]:
        """
        Get courses that conflict with the given course.
        """
        if self.conflict_manager:
            return set(self.conflict_manager.get_conflicts(course_id))
        instances = self.get_course(course_id)
        if instances:
            return set(instances[0].conflicts)
        return set()


def display_courses(course_manager: CourseManager) -> None:
    """Display all courses in a formatted list."""
    print("\n" + "=" * 60)
    print("COURSE LIST")
    print("=" * 60)

    all_courses = course_manager.get_all_courses()
    if not all_courses:
        print("No courses found.")
        return

    for course_id, instances in all_courses.items():
        print(f"\n📖 {course_id}")
        for i, course in enumerate(instances):
            instance_label = f" (Instance {i + 1})" if len(instances) > 1 else ""
            print(f"   {instance_label}")
            print(f"   📊 Credits: {course.credits}")
            print(f"   🏢 Rooms: {', '.join(course.room) if course.room else 'None'}")
            print(f"   🔬 Labs: {', '.join(course.lab) if course.lab else 'None'}")
            print(f"   👤 Faculty: {', '.join(course.faculty) if course.faculty else 'Unassigned'}")
            print(f"   ⚠️  Conflicts: {', '.join(course.conflicts) if course.conflicts else 'None'}")
            if i < len(instances) - 1:
                print("   " + "-" * 40)

    print("=" * 60)


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
        conflict = input(f"  Conflict {len(conflicts) + 1} (or Enter to finish): ").strip()
        if not conflict:
            break
        conflicts.append(conflict)

    return {
        'course_id': course_id,
        'credits': credits,
        'room': rooms,
        'lab': labs,
        'faculty': faculty,
        'conflicts': conflicts
    }

def add_course_interactive(course_manager: CourseManager) -> None:
    """Interactive course addition."""
    try:
        course_data = get_course_input()
        course = Course(**course_data)
        course_manager.add_course(course)
        print(f"✅ Successfully added course: {course.course_id}")
    except Exception as e:
        print(f"❌ Error adding course: {e}")


def modify_course_interactive(course_manager: CourseManager) -> None:
    """Interactive course modification."""
    display_courses(course_manager)

    course_id = input("\nEnter Course ID to modify: ").strip()
    course_instances = course_manager.get_course(course_id)

    if not course_instances:
        print(f"❌ Course {course_id} not found.")
        return

    if len(course_instances) > 1:
        print(f"\nFound {len(course_instances)} instances of {course_id}:")
        for i, course in enumerate(course_instances):
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
    print(f"\n📝 MODIFYING: {current_course.course_id} (Instance {choice + 1})")

    # Get new values, showing current values as defaults
    print(f"\nCurrent credits: {current_course.credits}")
    credits_input = input("New credits (press Enter to keep current): ").strip()
    credits = int(credits_input) if credits_input else current_course.credits

    print(f"\nCurrent rooms: {', '.join(current_course.room) if current_course.room else 'None'}")
    print("Enter new rooms (press Enter to finish, 'keep' to keep current):")
    rooms_input = input("  New rooms (or 'keep'): ").strip().lower()
    if rooms_input == 'keep':
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
    print(f"\nCurrent labs: {', '.join(current_course.lab) if current_course.lab else 'None'}")
    labs_input = input("Enter new labs ('keep' to keep current, Enter for none): ").strip().lower()
    if labs_input == 'keep':
        labs = current_course.lab
    else:
        labs = []
        if labs_input and labs_input != 'keep':
            labs.append(labs_input)
            while True:
                lab = input(f"  Lab {len(labs) + 1} (or Enter to finish): ").strip()
                if not lab:
                    break
                labs.append(lab)

    print(f"\nCurrent faculty: {', '.join(current_course.faculty) if current_course.faculty else 'None'}")
    faculty_input = input("Enter new faculty ('keep' to keep current, Enter for none): ").strip().lower()
    if faculty_input == 'keep':
        faculty = current_course.faculty
    else:
        faculty = []
        if faculty_input and faculty_input != 'keep':
            faculty.append(faculty_input)
            while True:
                fac = input(f"  Faculty {len(faculty) + 1} (or Enter to finish): ").strip()
                if not fac:
                    break
                faculty.append(fac)

    print(f"\nCurrent conflicts: {', '.join(current_course.conflicts) if current_course.conflicts else 'None'}")
    conflicts_input = input("Enter new conflicts ('keep' to keep current, Enter for none): ").strip().lower()
    if conflicts_input == 'keep':
        conflicts = current_course.conflicts
    else:
        conflicts = []
        if conflicts_input and conflicts_input != 'keep':
            conflicts.append(conflicts_input)
            while True:
                conflict = input(f"  Conflict {len(conflicts) + 1} (or Enter to finish): ").strip()
                if not conflict:
                    break
                conflicts.append(conflict)

    # Remove old instance and add new one
    course_manager.delete_course(course_id, choice)
    new_course = Course(
        course_id=current_course.course_id,
        credits=credits,
        room=rooms,
        lab=labs,
        faculty=faculty,
        conflicts=conflicts
    )
    course_manager.add_course(new_course)

    print(f"✅ Successfully modified course: {current_course.course_id}")


def delete_course_interactive(course_manager: CourseManager) -> None:
    """Interactive course deletion."""
    display_courses(course_manager)

    course_id = input("\nEnter Course ID to delete: ").strip()
    course_instances = course_manager.get_course(course_id)

    if not course_instances:
        print(f"❌ Course {course_id} not found.")
        return

    if len(course_instances) > 1:
        print(f"\nFound {len(course_instances)} instances of {course_id}:")
        print("  0. Delete ALL instances")
        for i, course in enumerate(course_instances):
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
            # Delete all instances
            while course_manager.get_course(course_id):
                course_manager.delete_course(course_id, 0)
            print(f"✅ Successfully deleted all instances of course: {course_id}")
        else:
            course_manager.delete_course(course_id, choice - 1)
            print(f"✅ Successfully deleted instance {choice} of course: {course_id}")
    else:
        confirm = input(f"Are you sure you want to delete {course_id}? (y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            course_manager.delete_course(course_id, 0)
            print(f"✅ Successfully deleted course: {course_id}")
        else:
            print("Deletion cancelled.")


def course_management_menu(config: dict, config_file: str, time_slots: dict) -> dict:
    """Course management menu interface."""
    course_manager = CourseManager()
    course_manager.load_courses(config.get('courses', []))

    while True:
        print("\n" + "=" * 50)
        print("COURSE MANAGEMENT")
        print("=" * 50)
        print("1. 👀 View all courses")
        print("2. ➕ Add new course")
        print("3. ✏️  Modify existing course")
        print("4. ❌ Delete course")
        print("5. 💾 Save changes and exit")
        print("6. 🚪 Exit without saving")
        print("=" * 50)

        choice = input("Select an option (1-6): ").strip()

        if choice == '1':
            display_courses(course_manager)
        elif choice == '2':
            add_course_interactive(course_manager)
        elif choice == '3':
            modify_course_interactive(course_manager)
        elif choice == '4':
            delete_course_interactive(course_manager)
        elif choice == '5':
            # Save changes back to config
            updated_courses = []
            for course_instances in course_manager.get_all_courses().values():
                for course in course_instances:
                    updated_courses.append({
                        'course_id': course.course_id,
                        'credits': course.credits,
                        'room': course.room,
                        'lab': course.lab,
                        'faculty': course.faculty,
                        'conflicts': course.conflicts
                    })

                config['courses'] = updated_courses
                # Save changes to file
                import json
                full_config = {
                    "config": config,
                    "time_slot_config": time_slots
                }

                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(full_config, f, indent=2, ensure_ascii=False)

                print(f"✅ Configuration saved successfully to {config_file}")
                return config
        elif choice == '6':
         print("Exiting without saving changes.")
        return config
    else:
            print("Invalid choice. Please select 1-6.")