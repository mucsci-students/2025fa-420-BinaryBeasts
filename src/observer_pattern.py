"""
Observer Design Pattern Implementation for the Scheduler Project.

This module implements the Observer pattern to enable loose coupling between
components when data changes occur. It allows objects to be notified automatically
when the state of other objects changes, which is particularly useful in MVC
architectures for keeping views synchronized with model changes.

The Observer pattern consists of:
- Observable (Subject): The object being watched
- Observer: The object that wants to be notified of changes
- Event notifications: Messages sent when changes occur
"""

from abc import ABC, abstractmethod
from typing import List, Any, Dict
from enum import Enum


class EventType(Enum):
    """
    Enumeration of different types of events that can be observed.
    
    This provides type safety and prevents typos when registering for
    or emitting events.
    """
    # Course-related events
    COURSE_ADDED = "course_added"
    COURSE_UPDATED = "course_updated"
    COURSE_REMOVED = "course_removed"
    
    # Faculty-related events
    FACULTY_ADDED = "faculty_added"
    FACULTY_UPDATED = "faculty_updated"
    FACULTY_REMOVED = "faculty_removed"
    FACULTY_LOADED = "faculty_loaded"
    
    # Room-related events
    ROOM_ADDED = "room_added"
    ROOM_UPDATED = "room_updated"
    ROOM_REMOVED = "room_removed"
    
    # Lab-related events
    LAB_ADDED = "lab_added"
    LAB_UPDATED = "lab_updated"
    LAB_REMOVED = "lab_removed"


class Observer(ABC):
    """
    Abstract base class for all observers.
    
    Classes that want to observe events must inherit from this class
    and implement the update method.
    """
    
    @abstractmethod
    def update(self, event_type: EventType, data: Any = None) -> None:
        """
        Called when an observed event occurs.
        
        Args:
            event_type (EventType): The type of event that occurred
            data (Any, optional): Additional data associated with the event
        """
        pass


class Observable:
    """
    Base class for objects that can be observed.
    
    This class manages a list of observers and provides methods to
    add, remove, and notify observers when events occur.
    """
    
    def __init__(self):
        """Initialize the observable with an empty list of observers."""
        self._observers: List[Observer] = []
        self._event_filters: Dict[Observer, List[EventType]] = {}
    
    def add_observer(self, observer: Observer, event_types: List[EventType] = None) -> None:
        """
        Add an observer to be notified of events.
        
        Args:
            observer (Observer): The observer to add
            event_types (List[EventType], optional): Specific event types to observe.
                                                   If None, observer will receive all events.
        """
        if observer not in self._observers:
            self._observers.append(observer)
            
            # Store event filter for this observer
            if event_types is not None:
                self._event_filters[observer] = event_types
            else:
                # If no specific events, remove any existing filter
                self._event_filters.pop(observer, None)
    
    def remove_observer(self, observer: Observer) -> None:
        """
        Remove an observer from the notification list.
        
        Args:
            observer (Observer): The observer to remove
        """
        if observer in self._observers:
            self._observers.remove(observer)
            # Clean up event filter
            self._event_filters.pop(observer, None)
    
    def notify_observers(self, event_type: EventType, data: Any = None) -> None:
        """
        Notify all registered observers of an event.
        
        Args:
            event_type (EventType): The type of event that occurred
            data (Any, optional): Additional data to pass to observers
        """
        for observer in self._observers[:]:  # Create a copy to avoid modification during iteration
            try:
                # Check if observer has event filters
                if observer in self._event_filters:
                    # Only notify if event type is in the filter
                    if event_type in self._event_filters[observer]:
                        observer.update(event_type, data)
                else:
                    # No filter, notify of all events
                    observer.update(event_type, data)
                    
            except Exception as e:
                # Log the error but continue notifying other observers
                print(f"Error notifying observer {observer}: {e}")
    
    def get_observer_count(self) -> int:
        """
        Get the number of registered observers.
        
        Returns:
            int: The number of observers
        """
        return len(self._observers)
    
    def clear_observers(self) -> None:
        """Remove all observers."""
        self._observers.clear()
        self._event_filters.clear()


class EventData:
    """
    Container for event data with common attributes.
    
    This provides a structured way to pass data with events,
    making it easier to handle different types of events consistently.
    """
    
    def __init__(self, source: Any = None, old_value: Any = None, 
                 new_value: Any = None, **kwargs):
        """
        Initialize event data.
        
        Args:
            source (Any, optional): The object that triggered the event
            old_value (Any, optional): The previous value (for update events)
            new_value (Any, optional): The new value (for update events)
            **kwargs: Additional event-specific data
        """
        self.source = source
        self.old_value = old_value
        self.new_value = new_value
        self.extra_data = kwargs
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get additional data by key.
        
        Args:
            key (str): The key to look up
            default (Any, optional): Default value if key not found
            
        Returns:
            Any: The value associated with the key, or default
        """
        return self.extra_data.get(key, default)


# Convenience function for creating observers
def create_lambda_observer(callback_function) -> Observer:
    """
    Create an observer from a lambda function or callable.
    
    Args:
        callback_function: Function that takes (event_type, data) parameters
        
    Returns:
        Observer: An observer that calls the provided function
    """
    class LambdaObserver(Observer):
        def __init__(self, callback):
            self.callback = callback
        
        def update(self, event_type: EventType, data: Any = None) -> None:
            self.callback(event_type, data)
    
    return LambdaObserver(callback_function)