"""
Conflict Resolution Observer for Cross-Manager Dependencies.

This module implements observers that handle conflicts and dependencies
between different managers. For example, when a faculty member is deleted,
it ensures that all courses referencing that faculty are updated accordingly.
"""

from src.observer_pattern import Observer, EventType, EventData
from typing import Dict, Any, List


class ConflictResolutionObserver(Observer):
    """
    Observer that handles conflicts and dependencies between managers.
    
    This observer listens to events from one manager and takes appropriate
    actions in other managers to maintain data consistency and prevent conflicts.
    """
    
    def __init__(self):
        """Initialize the conflict resolution observer."""
        self.managers = {}  # Store references to all managers
        self.combined_configs = []  # Store references to CombinedConfig objects
    
    def register_manager(self, manager_type: str, manager) -> None:
        """
        Register a manager to be monitored and managed for conflicts.
        
        Args:
            manager_type (str): Type of manager ('course', 'faculty', 'lab', 'room')
            manager: The manager instance
        """
        self.managers[manager_type] = manager
    
    def register_combined_config(self, combined_config) -> None:
        """
        Register a CombinedConfig object to be updated when conflicts are resolved.
        
        Args:
            combined_config: The CombinedConfig object to keep in sync
        """
        if combined_config not in self.combined_configs:
            self.combined_configs.append(combined_config)
    
    def update(self, event_type: EventType, data: EventData = None) -> None:
        """
        Handle events and resolve conflicts across managers.
        
        Args:
            event_type (EventType): The type of event that occurred
            data (EventData): Additional event data
        """
        try:
            # Handle faculty deletion - check and update courses
            if event_type == EventType.FACULTY_REMOVED:
                self._handle_faculty_removal(data)
            
            # Handle lab deletion - check and update courses
            elif event_type == EventType.LAB_REMOVED:
                self._handle_lab_removal(data)
            
            # Handle room deletion - check and update courses
            elif event_type == EventType.ROOM_REMOVED:
                self._handle_room_removal(data)
            
            # Handle faculty name update - update course references
            elif event_type == EventType.FACULTY_UPDATED:
                self._handle_faculty_update(data)
            
            # Handle lab name update - update course references  
            elif event_type == EventType.LAB_UPDATED:
                self._handle_lab_update(data)
            
            # Handle room name update - update course references
            elif event_type == EventType.ROOM_UPDATED:
                self._handle_room_update(data)
                
        except Exception as e:
            print(f"Error in ConflictResolutionObserver: {e}")
    
    def _handle_faculty_removal(self, data: EventData) -> None:
        """
        Handle faculty removal by updating all courses that reference the deleted faculty.
        
        Args:
            data (EventData): Event data containing the removed faculty information
        """
        if not data or not data.old_value:
            return
        
        removed_faculty_name = data.old_value.name
        course_manager = self.managers.get('course')
        
        if not course_manager:
            return
        
        # Check all courses for references to the deleted faculty
        for course_instances in course_manager.courses.values():
            for course in course_instances:
                if removed_faculty_name in course.faculty:
                    # Remove the faculty reference from the course
                    course.faculty = [f for f in course.faculty if f != removed_faculty_name]
        
        # Update any registered CombinedConfig objects
        self._update_combined_configs_faculty_removal(removed_faculty_name)
    
    def _handle_lab_removal(self, data: EventData) -> None:
        """
        Handle lab removal by updating all courses that reference the deleted lab.
        
        Args:
            data (EventData): Event data containing the removed lab information
        """
        if not data or not data.old_value:
            return
        
        removed_lab_name = data.old_value
        course_manager = self.managers.get('course')
        
        if not course_manager:
            return
        
        # Check all courses for references to the deleted lab
        for course_instances in course_manager.courses.values():
            for course in course_instances:
                if removed_lab_name in course.lab:
                    # Remove the lab reference from the course
                    course.lab = [l for l in course.lab if l != removed_lab_name]
    
    def _handle_room_removal(self, data: EventData) -> None:
        """
        Handle room removal by updating all courses that reference the deleted room.
        
        Args:
            data (EventData): Event data containing the removed room information
        """
        if not data or not data.old_value:
            return
        
        removed_room_name = data.old_value
        course_manager = self.managers.get('course')
        
        if not course_manager:
            return
        
        # Check all courses for references to the deleted room
        for course_instances in course_manager.courses.values():
            for course in course_instances:
                if removed_room_name in course.room:
                    # Remove the room reference from the course
                    course.room = [r for r in course.room if r != removed_room_name]
    
    def _handle_faculty_update(self, data: EventData) -> None:
        """
        Handle faculty name changes by updating course references.
        
        Args:
            data (EventData): Event data containing old and new faculty information
        """
        if not data or not data.old_value or not data.new_value:
            return
        
        old_name = data.old_value.name
        new_name = data.new_value.name
        
        if old_name == new_name:
            return  # No name change
        
        course_manager = self.managers.get('course')
        if not course_manager:
            return
        
        updates_made = []
        
        # Update all course references from old name to new name
        for course_instances in course_manager.courses.values():
            for course in course_instances:
                if old_name in course.faculty:
                    # Replace old faculty name with new name
                    course.faculty = [new_name if f == old_name else f for f in course.faculty]
        
        # Updates made silently - no logging needed for name changes
    
    def _handle_lab_update(self, data: EventData) -> None:
        """Handle lab name changes by updating course references."""
        if not data or not data.old_value or not data.new_value:
            return
        
        old_name = data.old_value
        new_name = data.new_value
        
        course_manager = self.managers.get('course')
        if not course_manager:
            return
        
        for course_instances in course_manager.courses.values():
            for course in course_instances:
                if old_name in course.lab:
                    course.lab = [new_name if l == old_name else l for l in course.lab]
    
    def _handle_room_update(self, data: EventData) -> None:
        """Handle room name changes by updating course references."""
        if not data or not data.old_value or not data.new_value:
            return
        
        old_name = data.old_value
        new_name = data.new_value
        
        course_manager = self.managers.get('course')
        if not course_manager:
            return
        
        for course_instances in course_manager.courses.values():
            for course in course_instances:
                if old_name in course.room:
                    course.room = [new_name if r == old_name else r for r in course.room]
    
    def _update_combined_configs_faculty_removal(self, removed_faculty_name: str) -> None:
        """
        Update all registered CombinedConfig objects to remove faculty references from courses.
        
        Args:
            removed_faculty_name (str): Name of the faculty member that was removed
        """
        for combined_config in self.combined_configs:
            try:
                # Update courses in the CombinedConfig to remove faculty references
                for course in combined_config.config.courses:
                    if hasattr(course, 'faculty') and isinstance(course.faculty, list):
                        if removed_faculty_name in course.faculty:
                            course.faculty = [f for f in course.faculty if f != removed_faculty_name]
            except Exception as e:
                # Log error but continue with other configs
                print(f"Warning: Failed to update CombinedConfig for faculty removal: {e}")