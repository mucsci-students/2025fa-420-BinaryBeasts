# comment
from dataclasses import field
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

        # Optional lists (use [] if not provided)
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
        # Start with clean sets to avoid stale entries
        self.rooms.clear()
        self.labs.clear()
        self.faculty.clear()
        # Loop through all instances of all courses
        for instances in self.courses.values():
            for course in instances:
                # Add each course's resources
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

#TODO
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

    def course_exists(self, value: str) -> bool:
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


    def load_course_manager_from_config(config: Dict) -> "CourseManager":
        course_data = config.get("courses", [])
        course_manager = CourseManager()
        course_manager.load_courses(course_data)
        try:
            # placeholder for loading conflict manager if available
            from configparser import load_course_manager_from_config as load_conf_mgr
            course_manager.conflict_manager = load_conf_mgr(config)
        except Exception as e:
            print(f"Warning: could not load conflict manager {e}")
        return course_manager


    def print_course_summary(self) -> None:
        """
        Print a summary of all courses.

        Displays each course_id and its instances with fields.
        Also prints statistics at the end.
        """
        print("Course Summary")
        print("=" * 60)

        for course_id, course_instances in sorted(self.courses.items()):
            print(f"\n{course_id}:")
            for i, course in enumerate(course_instances):
                instance_label = f" (Instance {i+1})" if len(course_instances) > 1 else ""
                print(f"  Credits: {course.credits}{instance_label}")
                print(f"  Room: {', '.join(course.room) if course.room else 'None'}")
                print(f"  Lab: {', '.join(course.lab) if course.lab else 'None'}")
                print(f"  Faculty: {', '.join(course.faculty) if course.faculty else 'None'}")
                print(f"  Conflicts: {', '.join(course.conflicts) if course.conflicts else 'None'}")
                if i < len(course_instances) - 1:
                    print("  " + "-" * 40)

        stats = self.get_course_statistics()
        print(f"\nTotal Courses: {stats['total_unique_courses']}")
        print(f"Total Instances: {stats['total_course_instances']}")
        print(f"Available Rooms: {stats['total_rooms']}")
        print(f"Available Labs: {stats['total_labs']}")
        print(f"Faculty Count: {stats['total_faculty']}")

