import json
import pytest

from src.models.room_model import RoomManager
from src.controllers.room_controller import RoomController


def test_room_manager_creation():
    """Test basic RoomManager creation and initialization."""
    manager = RoomManager()
    assert manager is not None
    assert manager.rooms == []


def test_room_manager_basic_operations():
    """Test basic RoomManager functionality."""
    mgr = RoomManager()

    # Add rooms (RoomManager works with room names as strings)
    assert mgr.add_room("Room A") is True
    assert mgr.add_room("Room B") is True
    
    # Check duplicate prevention
    assert mgr.add_room("Room A") is False  # Already exists
    
    # Get rooms
    rooms = mgr.get_rooms()
    assert "Room A" in rooms
    assert "Room B" in rooms
    
    # Check room existence
    assert mgr.room_exists("Room A") is True
    assert mgr.room_exists("Room C") is False


def test_room_manager_edit_delete():
    """Test editing and deleting rooms."""
    mgr = RoomManager()
    
    # Add initial room
    mgr.add_room("Room C")
    
    # Edit room (rename)
    assert mgr.edit_room("Room C", "Room D") is True
    
    # Verify edit
    assert mgr.room_exists("Room D") is True
    assert mgr.room_exists("Room C") is False
    
    # Delete room
    assert mgr.delete_room("Room D") is True
    assert mgr.room_exists("Room D") is False
    
    # Try to delete non-existent room
    assert mgr.delete_room("Room X") is False


def test_room_controller_basic_flow(tmp_path):
    """Test RoomController basic operations."""
    mgr = RoomManager()
    controller = RoomController(mgr)

    # Add room via controller (room names are strings)
    assert controller.add_room("Roddy 140") is True
    
    # Check it exists
    rooms = controller.get_rooms()
    assert "Roddy 140" in rooms
    
    # Check room existence via controller
    assert controller.room_exists("Roddy 140") is True
    
    # Room controller doesn't have save_to_file method
    # Instead test that controller has expected functionality
    assert hasattr(controller, 'get_rooms')
    assert hasattr(controller, 'room_exists')


def test_room_controller_edit_delete():
    """Test editing and deleting rooms through controller."""
    mgr = RoomManager()
    controller = RoomController(mgr)

    # Add initial room
    controller.add_room("Lab 1")
    assert "Lab 1" in controller.get_rooms()
    
    # Edit room (rename)
    assert controller.edit_room("Lab 1", "Lab 2") is True
    
    # Verify edit
    assert "Lab 2" in controller.get_rooms()
    assert "Lab 1" not in controller.get_rooms()
    
    # Delete room
    assert controller.delete_room("Lab 2") is True
    assert "Lab 2" not in controller.get_rooms()
