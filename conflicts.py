#!/usr/bin/env python3
"""
Organizing and creating conflicts
Adding, modifying, deleting conflicts and updating the database
so that current conflicts are known in the scheduler.
"""

from typing import Dict, List, Set, Tuple, Optional


class ConflictManager:
    """
    Manages course conflicts for the scheduling system.
    Handles detection, validation, and resolution of course conflicts.
    """
    
    def __init__(self, courses: List[Dict]):
        """
        Initialize the conflict manager with course data.
        
        Args:
            courses: List of course dictionaries from the config
        """
        self.courses = courses
        self.conflict_map = self._build_conflict_map()
    
    def _build_conflict_map(self) -> Dict[str, Set[str]]:
        """
        Build a mapping of course conflicts from the course data.
        
        Returns:
            Dictionary mapping course IDs to sets of conflicting course IDs
        """
        conflict_map = {}
        
        for course in self.courses:
            course_id = course.get("course_id")
            conflicts = course.get("conflicts", [])
            
            if course_id:
                if course_id not in conflict_map:
                    conflict_map[course_id] = set()
                
                # Add conflicts for this course
                for conflict_course in conflicts:
                    conflict_map[course_id].add(conflict_course)
                    
                    # Ensure bidirectional conflicts
                    if conflict_course not in conflict_map:
                        conflict_map[conflict_course] = set()
                    conflict_map[conflict_course].add(course_id)
        
        return conflict_map
    
    def has_conflict(self, course1: str, course2: str) -> bool:
        """
        Check if two courses have a conflict.
        
        Args:
            course1: First course ID
            course2: Second course ID
            
        Returns:
            True if courses conflict, False otherwise
        """
        if course1 not in self.conflict_map:
            return False
        return course2 in self.conflict_map[course1]
    
    def get_conflicts(self, course_id: str) -> Set[str]:
        """
        Get all courses that conflict with the given course.
        
        Args:
            course_id: The course ID to check conflicts for
            
        Returns:
            Set of conflicting course IDs
        """
        return self.conflict_map.get(course_id, set())
    
    def add_conflict(self, course1: str, course2: str) -> None:
        """
        Add a conflict between two courses.
        
        Args:
            course1: First course ID
            course2: Second course ID
        """
        if course1 not in self.conflict_map:
            self.conflict_map[course1] = set()
        if course2 not in self.conflict_map:
            self.conflict_map[course2] = set()
        
        self.conflict_map[course1].add(course2)
        self.conflict_map[course2].add(course1)
    
    def remove_conflict(self, course1: str, course2: str) -> None:
        """
        Remove a conflict between two courses.
        
        Args:
            course1: First course ID
            course2: Second course ID
        """
        if course1 in self.conflict_map:
            self.conflict_map[course1].discard(course2)
        if course2 in self.conflict_map:
            self.conflict_map[course2].discard(course1)
    
    def validate_schedule_conflicts(self, schedule: List[Dict]) -> List[Tuple[str, str]]:
        """
        Validate a schedule for conflicts and return any found.
        
        Args:
            schedule: List of scheduled course dictionaries
            
        Returns:
            List of tuples representing conflicting course pairs
        """
        conflicts_found = []
        scheduled_courses = []
        
        for item in schedule:
            course_id = item.get("course_id")
            if course_id:
                scheduled_courses.append(course_id)
        
        # Check all pairs for conflicts
        for i in range(len(scheduled_courses)):
            for j in range(i + 1, len(scheduled_courses)):
                course1 = scheduled_courses[i]
                course2 = scheduled_courses[j]
                
                if self.has_conflict(course1, course2):
                    conflicts_found.append((course1, course2))
        
        return conflicts_found
    
    def get_conflict_groups(self) -> List[Set[str]]:
        """
        Get groups of courses that are all in conflict with each other.
        
        Returns:
            List of sets, each containing courses that conflict with each other
        """
        visited = set()
        conflict_groups = []
        
        def dfs(course: str, group: Set[str]):
            if course in visited:
                return
            visited.add(course)
            group.add(course)
            
            # Visit all conflicting courses
            for conflict_course in self.conflict_map.get(course, set()):
                dfs(conflict_course, group)
        
        for course in self.conflict_map:
            if course not in visited:
                group = set()
                dfs(course, group)
                if group:
                    conflict_groups.append(group)
        
        return conflict_groups
    
    def can_schedule_together(self, courses: List[str]) -> bool:
        """
        Check if a list of courses can be scheduled together (no conflicts).
        
        Args:
            courses: List of course IDs
            
        Returns:
            True if no conflicts exist, False otherwise
        """
        for i in range(len(courses)):
            for j in range(i + 1, len(courses)):
                if self.has_conflict(courses[i], courses[j]):
                    return False
        return True
    
    def get_maximum_independent_set(self, course_subset: Optional[List[str]] = None) -> Set[str]:
        """
        Find the maximum set of courses that can be scheduled without conflicts.
        Greedy approach for the maximum independent set problem.
        
        Args:
            course_subset: Optional subset of courses to consider
            
        Returns:
            Set of course IDs that can be scheduled together
        """
        if course_subset is None:
            available_courses = list(self.conflict_map.keys())
        else:
            available_courses = course_subset.copy()
        
        # Sort by number of conflicts (ascending)
        available_courses.sort(key=lambda x: len(self.conflict_map.get(x, set())))
        
        independent_set = set()
        
        for course in available_courses:
            # Check if this course conflicts with any already selected
            conflicts_with_selected = any(
                self.has_conflict(course, selected) 
                for selected in independent_set
            )
            
            if not conflicts_with_selected:
                independent_set.add(course)
        
        return independent_set
    
    def print_conflict_summary(self) -> None:
        """
        Print a summary of all conflicts in the system.
        """
        print("Course Conflict Summary:")
        print("=" * 50)
        
        for course, conflicts in sorted(self.conflict_map.items()):
            if conflicts:
                conflict_list = ", ".join(sorted(conflicts))
                print(f"{course}: {conflict_list}")
            else:
                print(f"{course}: No conflicts")
        
        print(f"\nTotal courses: {len(self.conflict_map)}")
        total_conflicts = sum(len(conflicts) for conflicts in self.conflict_map.values()) // 2
        print(f"Total conflict pairs: {total_conflicts}")


def load_conflicts_from_config(config: Dict) -> ConflictManager:
    """
    Create a ConflictManager from configuration data.
    
    Args:
        config: Configuration dictionary containing courses
        
    Returns:
        Initialized ConflictManager instance
    """
    courses = config.get("courses", [])
    return ConflictManager(courses)


def detect_conflicting_assignments(schedule: List[Dict], conflict_manager: ConflictManager) -> Dict:
    """
    Detect conflicting course assignments in a schedule.
    
    Args:
        schedule: List of scheduled course assignments
        conflict_manager: ConflictManager instance
        
    Returns:
        Dictionary containing conflict analysis
    """
    conflicts = conflict_manager.validate_schedule_conflicts(schedule)
    
    analysis = {
        "has_conflicts": len(conflicts) > 0,
        "conflict_count": len(conflicts),
        "conflicting_pairs": conflicts,
        "courses_with_conflicts": set()
    }
    
    # Track which courses are involved in conflicts
    for course1, course2 in conflicts:
        analysis["courses_with_conflicts"].add(course1)
        analysis["courses_with_conflicts"].add(course2)
    
    analysis["courses_with_conflicts"] = list(analysis["courses_with_conflicts"])
    
    return analysis


def suggest_conflict_resolution(conflicts: List[Tuple[str, str]], 
                              schedule: List[Dict],
                              conflict_manager: ConflictManager) -> List[str]:
    """
    Suggest ways to resolve scheduling conflicts.
    
    Args:
        conflicts: List of conflicting course pairs
        schedule: Current schedule
        conflict_manager: ConflictManager instance
        
    Returns:
        List of suggested resolution strategies
    """
    suggestions = []
    
    if not conflicts:
        return ["No conflicts detected in schedule."]
    
    # Count how many conflicts each course is involved in
    conflict_counts = {}
    for course1, course2 in conflicts:
        conflict_counts[course1] = conflict_counts.get(course1, 0) + 1
        conflict_counts[course2] = conflict_counts.get(course2, 0) + 1
    
    # Suggest removing the course with the most conflicts
    if conflict_counts:
        most_problematic = max(conflict_counts.items(), key=lambda x: x[1])
        suggestions.append(
            f"Consider removing or rescheduling '{most_problematic[0]}' "
            f"which is involved in {most_problematic[1]} conflict(s)."
        )
    
    # Suggest alternative scheduling
    suggestions.append("Consider scheduling conflicting courses in different time slots.")
    suggestions.append("Review course prerequisites and dependencies for alternative arrangements.")
    
    return suggestions