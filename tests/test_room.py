from unittest.mock import Mock

from src.models.room_model import RoomManager
from src.controllers.room_controller import RoomController


def test_room_manager_creation():
    """Test basic RoomManager creation and initialization."""
    mock_config = Mock()
    mock_config.config = Mock()
    mock_config.config.rooms = []

    manager = RoomManager(mock_config)
    assert manager is not None
    assert manager.rooms == []


def test_room_manager_basic_operations():
    """Test basic RoomManager functionality."""
    mock_config = Mock()
    mock_config.config = Mock()
    mock_config.config.rooms = []

    mgr = RoomManager(mock_config)

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
    mock_config = Mock()
    mock_config.config = Mock()
    mock_config.config.rooms = []

    mgr = RoomManager(mock_config)
    
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
    mock_config = Mock()
    mock_config.config = Mock()
    mock_config.config.rooms = []

    mgr = RoomManager(mock_config)
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
    mock_config = Mock()
    mock_config.config = Mock()
    mock_config.config.rooms = []

    mgr = RoomManager(mock_config)
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


def test_load_rooms_with_scheduler_config():
    """Test loading rooms from SchedulerConfig (not CombinedConfig)."""
    # Create a mock config with rooms directly (SchedulerConfig style)
    mock_config = Mock(spec=['rooms'])  # Only has 'rooms' attribute
    mock_config.rooms = ["Room1", "Room2", "Room3"]

    mgr = RoomManager(mock_config)

    # Assert: Rooms should be loaded from config.rooms
    rooms = mgr.get_rooms()
    assert len(rooms) == 3
    assert "Room1" in rooms


def test_load_rooms_with_no_rooms_attribute():
    """Test handling config with no rooms attribute."""
    # Create a mock config with neither config.rooms nor rooms
    mock_config = Mock(spec=[])  # No attributes

    mgr = RoomManager(mock_config)

    # Assert: Should initialize with empty list
    rooms = mgr.get_rooms()
    assert len(rooms) == 0


def test_add_empty_room():
    """Test adding empty room name should raise error."""
    import pytest

    mock_config = Mock()
    mock_config.config = Mock()
    mock_config.config.rooms = []

    mgr = RoomManager(mock_config)

    with pytest.raises(ValueError, match="Room name cannot be empty"):
        mgr.add_room("")


def test_edit_room_empty_new_name():
    """Test editing to empty name should raise error."""
    import pytest

    mock_config = Mock()
    mock_config.config = Mock()
    mock_config.config.rooms = ["Room A"]

    mgr = RoomManager(mock_config)

    with pytest.raises(ValueError, match="New room name cannot be empty"):
        mgr.edit_room("Room A", "")


def test_edit_nonexistent_room():
    """Test editing room that doesn't exist should fail."""
    mock_config = Mock()
    mock_config.config = Mock()
    mock_config.config.rooms = ["Room A"]

    mgr = RoomManager(mock_config)

    result = mgr.edit_room("Room X", "Room Y")
    assert result is False


def test_edit_to_existing_name():
    """Test editing to an existing name should fail."""
    mock_config = Mock()
    mock_config.config = Mock()
    mock_config.config.rooms = ["Room A", "Room B"]

    mgr = RoomManager(mock_config)

    result = mgr.edit_room("Room A", "Room B")
    assert result is False


def test_set_rooms():
    """Test setting rooms should replace all rooms."""
    mock_config = Mock()
    mock_config.config = Mock()
    mock_config.config.rooms = ["Old Room"]

    mgr = RoomManager(mock_config)

    new_rooms = ["Room X", "Room Y", "Room Z"]
    mgr.set_rooms(new_rooms)

    rooms = mgr.get_rooms()
    assert len(rooms) == 3
    assert "Room X" in rooms
    assert "Room Y" in rooms
    assert "Room Z" in rooms
    assert "Old Room" not in rooms


def test_to_dict():
    """Test converting rooms to dictionary format."""
    mock_config = Mock()
    mock_config.config = Mock()
    mock_config.config.rooms = ["Room A", "Room B"]

    mgr = RoomManager(mock_config)

    result = mgr.to_dict()

    assert isinstance(result, dict)
    assert "rooms" in result
    assert len(result["rooms"]) == 2
    assert "Room A" in result["rooms"]


def test_save_config():
    """Test updating config dictionary with room data."""
    mock_config = Mock()
    mock_config.config = Mock()
    mock_config.config.rooms = ["Room A", "Room B"]

    mgr = RoomManager(mock_config)

    config = {"courses": [], "labs": []}
    result = mgr.save_config(config)

    assert "rooms" in result
    assert len(result["rooms"]) == 2
    assert "Room A" in result["rooms"]
    assert "Room B" in result["rooms"]


def test_save_with_combined_config():
    """Test updating CombinedConfig object with room data."""
    mock_config = Mock()
    mock_config.config = Mock()
    mock_config.config.rooms = ["Room A", "Room B"]

    mgr = RoomManager(mock_config)

    # Create mock CombinedConfig
    mock_combined_config = Mock()
    mock_combined_config.config = Mock()
    mock_combined_config.config.rooms = []

    result = mgr.save_with_combined_config(mock_combined_config)

    assert len(result.config.rooms) == 2
    assert "Room A" in result.config.rooms


def test_update_room_references_in_courses():
    """Test updating room references in courses when room is renamed."""
    mock_config = Mock()
    mock_config.config = Mock()
    mock_config.config.rooms = []

    mgr = RoomManager(mock_config)

    # Create mock course objects
    mock_course1 = Mock()
    mock_course1.room = ["Room A", "Room B"]
    mock_course2 = Mock()
    mock_course2.room = ["Room A"]

    courses_dict = {
        "CMSC 140": [mock_course1],
        "CMSC 161": [mock_course2]
    }
    faculty_dict = {}

    # Update room references
    mgr.update_room_references("Room A", "Room X", courses_dict, faculty_dict)

    # Assert: Room A should be replaced with Room X
    assert "Room X" in mock_course1.room
    assert "Room A" not in mock_course1.room
    assert "Room X" in mock_course2.room


def test_update_room_references_in_faculty():
    """Test updating room preferences in faculty when room is renamed."""
    mock_config = Mock()
    mock_config.config = Mock()
    mock_config.config.rooms = []

    mgr = RoomManager(mock_config)

    # Create mock faculty objects
    mock_faculty1 = Mock()
    mock_faculty1.room_preferences = {"Room A": 5, "Room B": 3}
    mock_faculty2 = Mock()
    mock_faculty2.room_preferences = {"Room A": 8}

    courses_dict = {}
    faculty_dict = {
        "Dr. Smith": mock_faculty1,
        "Dr. Jones": mock_faculty2
    }

    # Update room references
    mgr.update_room_references("Room A", "Room X", courses_dict, faculty_dict)

    # Assert: Room A preference should be replaced with Room X
    assert "Room X" in mock_faculty1.room_preferences
    assert mock_faculty1.room_preferences["Room X"] == 5
    assert "Room A" not in mock_faculty1.room_preferences
    assert "Room X" in mock_faculty2.room_preferences


def test_remove_room_references_from_courses():
    """Test removing room references from courses when room is deleted."""
    mock_config = Mock()
    mock_config.config = Mock()
    mock_config.config.rooms = []

    mgr = RoomManager(mock_config)

    # Create mock course objects
    mock_course1 = Mock()
    mock_course1.room = ["Room A", "Room B"]
    mock_course2 = Mock()
    mock_course2.room = ["Room A"]

    courses_dict = {
        "CMSC 140": [mock_course1],
        "CMSC 161": [mock_course2]
    }
    faculty_dict = {}

    # Remove room references
    mgr.remove_room_references("Room A", courses_dict, faculty_dict)

    # Assert: Room A should be removed
    assert "Room A" not in mock_course1.room
    assert "Room B" in mock_course1.room
    assert "Room A" not in mock_course2.room


def test_remove_room_references_from_faculty():
    """Test removing room preferences from faculty when room is deleted."""
    mock_config = Mock()
    mock_config.config = Mock()
    mock_config.config.rooms = []

    mgr = RoomManager(mock_config)

    # Create mock faculty objects
    mock_faculty1 = Mock()
    mock_faculty1.room_preferences = {"Room A": 5, "Room B": 3}
    mock_faculty2 = Mock()
    mock_faculty2.room_preferences = {"Room A": 8}

    courses_dict = {}
    faculty_dict = {
        "Dr. Smith": mock_faculty1,
        "Dr. Jones": mock_faculty2
    }

    # Remove room references
    mgr.remove_room_references("Room A", courses_dict, faculty_dict)

    # Assert: Room A preference should be removed
    assert "Room A" not in mock_faculty1.room_preferences
    assert "Room B" in mock_faculty1.room_preferences
    assert "Room A" not in mock_faculty2.room_preferences
