# src/models/course_model.py

import json
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
        self.course_id = course_id
        self.credits = credits

        self.room = room if room is not None else []
        self.lab = lab if lab is not None else []
        self.conflicts = conflicts if conflicts is not None else []
        self.faculty = faculty if faculty is not None else []

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

    def to_dict(self) -> list:
        """Convert courses to dictionary format."""
        courses = []
        for course_instances in self.get_all_courses().values():
            for course in course_instances:
                courses.append({
                    'course_id': course.course_id,
                    'credits': course.credits,
                    'room': course.room,
                    'lab': course.lab,
                    'faculty': course.faculty,
                    'conflicts': course.conflicts
                })
        return courses

    def save_config(self, config: dict, time_slots: dict, config_file: str) -> bool:
        """Save configuration to file (for CLI)."""
        try:
            config['courses'] = self.to_dict()
            full_config = {
                "config": config,
                "time_slot_config": time_slots
            }
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(full_config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def save_with_combined_config(self, combined_config) -> bool:
        """Save courses to CombinedConfig (for GUI)."""
        try:
            from scheduler.config import CourseConfig

            with combined_config.edit_mode() as editable_config:
                # Clear existing courses
                editable_config.config.courses.clear()

                # Add all courses from this manager
                all_courses = self.get_all_courses()
                for course_id in all_courses:
                    for course in all_courses[course_id]:
                        new_course = CourseConfig(
                            course_id=course.course_id,
                            credits=course.credits,
                            room=course.room,
                            lab=course.lab,
                            faculty=course.faculty,
                            conflicts=course.conflicts
                        )
                        editable_config.config.courses.append(new_course)
            return True
        except Exception as e:
            print(f"Error saving: {e}")
            return False






