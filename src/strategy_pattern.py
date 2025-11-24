"""
Strategy Pattern for Schedule Optimization.

Defines different optimization strategies that can be swapped at runtime.
This is the SIMPLEST design pattern to implement - only ~45 lines!

Works with the actual config format where optimizer_flags is a list of strings:
["faculty_course", "faculty_room", "faculty_lab", "same_room", "same_lab", "pack_rooms"]
"""

from abc import ABC, abstractmethod
from typing import List


class OptimizationStrategy(ABC):
    """Abstract strategy for schedule optimization."""
    
    @abstractmethod
    def get_flags(self) -> List[str]:
        """Return list of optimizer flag strings."""
        pass


class PackingStrategy(OptimizationStrategy):
    """Pack courses into fewer rooms/labs."""
    
    def get_flags(self) -> List[str]:
        return ["pack_rooms", "pack_labs"]


class StabilityStrategy(OptimizationStrategy):
    """Keep courses in same rooms/labs."""
    
    def get_flags(self) -> List[str]:
        return ["same_room", "same_lab"]


class PreferenceStrategy(OptimizationStrategy):
    """Optimize by faculty preferences."""
    
    def get_flags(self) -> List[str]:
        return ["faculty_course", "faculty_room", "faculty_lab"]


class BalancedStrategy(OptimizationStrategy):
    """Balanced optimization with preferences and stability."""
    
    def get_flags(self) -> List[str]:
        return ["faculty_course", "same_room"]
