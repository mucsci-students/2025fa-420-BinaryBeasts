#!/usr/bin/env python3
"""
Course Manager
Manages course data, operations, and relationships for the scheduling system.
Handles course CRUD operations, filtering, validation, and integration with conflicts.
"""

from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass
from conflicts import ConflictManager


@dataclass
class Course:
    """
    Represents a single course with all its properties.
    """
    course_id: str
    credits: int
    room: List[str]
    lab: List[str]
    conflicts: List[str]
    faculty: List[str]
    
    def __post_init__(self):
        """Validate course data after initialization."""
        if not self.course_id:
            raise ValueError("Course ID cannot be empty")
        if self.credits <= 0:
            raise ValueError("Credits must be positive")


class CourseManager:
    """
    Manages all course-related operations for the scheduling system.
    Provides CRUD operations, filtering, validation, and conflict integration.
    """
    
    def __init__(self, courses_data: List[Dict]):
        """
        Initialize the course manager with course data.
        
        Args:
            courses_data: List of course dictionaries from config
        """
        self.courses = {}
        self.rooms = set()
        self.labs = set()
        self.faculty_members = set()
        self.conflict_manager = None
        
        self._load_courses(courses_data)
        self._extract_resources()
    
    def _load_courses(self, courses_data: List[Dict]) -> None:
        """
        Load courses from configuration data.
        
        Args:
            courses_data: List of course dictionaries
        """
        for course_data in courses_data:
            try:
                course = Course(
                    course_id=course_data.get("course_id", ""),
                    credits=course_data.get("credits", 0),
                    room=course_data.get("room", []),
                    lab=course_data.get("lab", []),
                    conflicts=course_data.get("conflicts", []),
                    faculty=course_data.get("faculty", [])
                )
                
                # Handle multiple instances of the same course
                if course.course_id not in self.courses:
                    self.courses[course.course_id] = []
                self.courses[course.course_id].append(course)
                
            except ValueError as e:
                print(f"Warning: Skipping invalid course data: {e}")
    
    def _extract_resources(self) -> None:
        """Extract all unique rooms, labs, and faculty from courses."""
        for course_instances in self.courses.values():
            for course in course_instances:
                self.rooms.update(course.room)
                self.labs.update(course.lab)
                self.faculty_members.update(course.faculty)
    
    def set_conflict_manager(self, conflict_manager: ConflictManager) -> None:
        """
        Set the conflict manager for this course manager.
        
        Args:
            conflict_manager: ConflictManager instance
        """
        self.conflict_manager = conflict_manager
    
    def get_course(self, course_id: str) -> List[Course]:
        """
        Get all instances of a course by ID.
        
        Args:
            course_id: The course ID to search for
            
        Returns:
            List of Course instances (empty if not found)
        """
        return self.courses.get(course_id, [])
    
    def get_all_courses(self) -> Dict[str, List[Course]]:
        """
        Get all courses managed by this manager.
        
        Returns:
            Dictionary mapping course IDs to lists of Course instances
        """
        return self.courses.copy()
    
    def get_course_ids(self) -> List[str]:
        """
        Get all unique course IDs.
        
        Returns:
            List of course IDs
        """
        return list(self.courses.keys())
    
    def add_course(self, course: Course) -> None:
        """
        Add a new course instance.
        Args:
            course: Course instance to add
        """
        if course.course_id not in self.courses:
            self.courses[course.course_id] = []
        self.courses[course.course_id].append(course)
        
        # Update resource sets
        self.rooms.update(course.room)
        self.labs.update(course.lab)
        self.faculty_members.update(course.faculty)
    
    def remove_course_instance(self, course_id: str, instance_index: int = 0) -> bool:
        """
        Remove a specific instance of a course.
        
        Args:
            course_id: The course ID
            instance_index: Index of the instance to remove
        Returns:
            True if removed successfully, False otherwise
        """
        if course_id not in self.courses:
            return False
        
        if 0 <= instance_index < len(self.courses[course_id]):
            self.courses[course_id].pop(instance_index)
            
            # Remove course ID if no instances left
            if not self.courses[course_id]:
                del self.courses[course_id]
            
            # Re-extract resources
            self._extract_resources()
            return True
        
        return False
    
    def filter_by_credits(self, credits: int) -> List[Course]:
        """
        Filter courses by credit hours.
        
        Args:
            credits: Number of credits to filter by
            
        Returns:
            List of Course instances with matching credits
        """
        results = []
        for course_instances in self.courses.values():
            for course in course_instances:
                if course.credits == credits:
                    results.append(course)
        return results
    
    def filter_by_room(self, room: str) -> List[Course]:
        """
        Filter courses that can be taught in a specific room.
        
        Args:
            room: Room name to filter by
            
        Returns:
            List of Course instances that can use the room
        """
        results = []
        for course_instances in self.courses.values():
            for course in course_instances:
                if room in course.room:
                    results.append(course)
        return results
    
    def filter_by_lab(self, lab: str) -> List[Course]:
        """
        Filter courses that require a specific lab.
        
        Args:
            lab: Lab name to filter by
            
        Returns:
            List of Course instances that require the lab
        """
        results = []
        for course_instances in self.courses.values():
            for course in course_instances:
                if lab in course.lab:
                    results.append(course)
        return results
    
    def filter_by_faculty(self, faculty_name: str) -> List[Course]:
        """
        Filter courses assigned to a specific faculty member.
        
        Args:
            faculty_name: Faculty member name to filter by
            
        Returns:
            List of Course instances assigned to the faculty
        """
        results = []
        for course_instances in self.courses.values():
            for course in course_instances:
                if faculty_name in course.faculty:
                    results.append(course)
        return results
    
    def get_courses_without_faculty(self) -> List[Course]:
        """
        Get courses that don't have any faculty assigned.
        
        Returns:
            List of Course instances without faculty assignments
        """
        results = []
        for course_instances in self.courses.values():
            for course in course_instances:
                if not course.faculty:
                    results.append(course)
        return results
    
    def get_courses_with_labs(self) -> List[Course]:
        """
        Get courses that require lab facilities.
        
        Returns:
            List of Course instances that require labs
        """
        results = []
        for course_instances in self.courses.values():
            for course in course_instances:
                if course.lab:
                    results.append(course)
        return results
    
    def get_available_rooms(self) -> Set[str]:
        """
        Get all available rooms from course data.
        
        Returns:
            Set of room names
        """
        return self.rooms.copy()
    
    def get_available_labs(self) -> Set[str]:
        """
        Get all available labs from course data.
        
        Returns:
            Set of lab names
        """
        return self.labs.copy()
    
    def get_faculty_members(self) -> Set[str]:
        """
        Get all faculty members from course data.
        
        Returns:
            Set of faculty names
        """
        return self.faculty_members.copy()
    
    def get_course_statistics(self) -> Dict[str, Any]:
        """
        Get statistical information about courses.
        
        Returns:
            Dictionary containing various statistics
        """
        total_instances = sum(len(instances) for instances in self.courses.values())
        credit_distribution = {}
        room_usage = {}
        lab_usage = {}
        
        for course_instances in self.courses.values():
            for course in course_instances:
                # Credit distribution
                credit_distribution[course.credits] = credit_distribution.get(course.credits, 0) + 1
                
                # Room usage
                for room in course.room:
                    room_usage[room] = room_usage.get(room, 0) + 1
                
                # Lab usage
                for lab in course.lab:
                    lab_usage[lab] = lab_usage.get(lab, 0) + 1
        
        return {
            "total_unique_courses": len(self.courses),
            "total_course_instances": total_instances,
            "total_rooms": len(self.rooms),
            "total_labs": len(self.labs),
            "total_faculty": len(self.faculty_members),
            "credit_distribution": credit_distribution,
            "room_usage": room_usage,
            "lab_usage": lab_usage,
            "courses_without_faculty": len(self.get_courses_without_faculty()),
            "courses_with_labs": len(self.get_courses_with_labs())
        }
    
    def validate_course_assignments(self) -> Dict[str, List[str]]:
        """
        Validate course assignments and identify potential issues.
        
        Returns:
            Dictionary containing validation results and issues
        """
        issues = {
            "courses_without_rooms": [],
            "courses_without_faculty": [],
            "invalid_credit_courses": [],
            "duplicate_course_instances": []
        }
        
        for course_id, course_instances in self.courses.items():
            for i, course in enumerate(course_instances):
                # Check for courses without rooms
                if not course.room:
                    issues["courses_without_rooms"].append(f"{course_id} (instance {i})")
                
                # Check for courses without faculty
                if not course.faculty:
                    issues["courses_without_faculty"].append(f"{course_id} (instance {i})")
                
                # Check for invalid credits
                if course.credits <= 0:
                    issues["invalid_credit_courses"].append(f"{course_id} (instance {i})")
            
            # Check for potential duplicate instances
            if len(course_instances) > 1:
                issues["duplicate_course_instances"].append(f"{course_id} ({len(course_instances)} instances)")
        
        return issues
    
    def get_conflicting_courses(self, course_id: str) -> Set[str]:
        """
        Get courses that conflict with the given course.
        
        Args:
            course_id: Course ID to check conflicts for
            
        Returns:
            Set of conflicting course IDs
        """
        if self.conflict_manager:
            return self.conflict_manager.get_conflicts(course_id)
        
        # Fallback to course's own conflict list
        course_instances = self.get_course(course_id)
        if course_instances:
            return set(course_instances[0].conflicts)
        
        return set()
    
    def can_schedule_together(self, course_ids: List[str]) -> bool:
        """
        Check if a list of courses can be scheduled together.
        
        Args:
            course_ids: List of course IDs to check
            
        Returns:
            True if courses can be scheduled together, False otherwise
        """
        if self.conflict_manager:
            return self.conflict_manager.can_schedule_together(course_ids)
        
        # Fallback implementation
        for i in range(len(course_ids)):
            for j in range(i + 1, len(course_ids)):
                course1_conflicts = set()
                course2_conflicts = set()
                
                course1_instances = self.get_course(course_ids[i])
                course2_instances = self.get_course(course_ids[j])
                
                if course1_instances:
                    course1_conflicts = set(course1_instances[0].conflicts)
                if course2_instances:
                    course2_conflicts = set(course2_instances[0].conflicts)
                
                if course_ids[j] in course1_conflicts or course_ids[i] in course2_conflicts:
                    return False
        
        return True
    
    def print_course_summary(self) -> None:
        """Print a summary of all courses and their properties."""
        print("Course Summary:")
        print("=" * 60)
        
        for course_id, course_instances in sorted(self.courses.items()):
            print(f"\n{course_id}:")
            for i, course in enumerate(course_instances):
                instance_label = f" (Instance {i+1})" if len(course_instances) > 1 else ""
                print(f"  Credits: {course.credits}{instance_label}")
                print(f"  Rooms: {', '.join(course.room) if course.room else 'None'}")
                print(f"  Labs: {', '.join(course.lab) if course.lab else 'None'}")
                print(f"  Faculty: {', '.join(course.faculty) if course.faculty else 'Unassigned'}")
                print(f"  Conflicts: {', '.join(course.conflicts) if course.conflicts else 'None'}")
                if i < len(course_instances) - 1:
                    print("  " + "-" * 40)
        
        stats = self.get_course_statistics()
        print(f"\nTotal Courses: {stats['total_unique_courses']}")
        print(f"Total Instances: {stats['total_course_instances']}")
        print(f"Available Rooms: {stats['total_rooms']}")
        print(f"Available Labs: {stats['total_labs']}")


def load_course_manager_from_config(config: Dict) -> CourseManager:
    """
    Create a CourseManager from configuration data.
    
    Args:
        config: Configuration dictionary containing courses
        
    Returns:
        Initialized CourseManager instance
    """
    courses_data = config.get("courses", [])
    course_manager = CourseManager(courses_data)
    
    # Optionally integrate with conflict manager
    try:
        from conflicts import load_conflicts_from_config
        conflict_manager = load_conflicts_from_config(config)
        course_manager.set_conflict_manager(conflict_manager)
    except ImportError:
        print("Warning: Could not load conflict manager")
    
    return course_manager