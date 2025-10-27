
from src.models.lab_model import LabManager
from src.controllers.lab_controller import LabController


def test_lab_manager_creation():
    """Test basic LabManager creation and initialization."""
    manager = LabManager()
    assert manager is not None
    assert manager.labs == []


def test_lab_manager_basic_operations():
    """Test basic LabManager operations."""
    manager = LabManager()
    
    # Add labs (LabManager works with lab names as strings)
    assert manager.add_lab("Linux Lab") is True
    assert manager.add_lab("Mac Lab") is True
    
    # Check duplicate prevention
    assert manager.add_lab("Linux Lab") is False  # Already exists
    
    # Get labs
    labs = manager.get_labs()
    assert "Linux Lab" in labs
    assert "Mac Lab" in labs
    
    # Check lab existence
    assert manager.lab_exists("Linux Lab") is True
    assert manager.lab_exists("Windows Lab") is False


def test_lab_manager_edit_delete():
    """Test editing and deleting labs."""
    manager = LabManager()
    
    # Add initial lab
    manager.add_lab("Test Lab")
    
    # Edit lab (rename)
    assert manager.edit_lab("Test Lab", "Advanced Lab") is True
    
    # Verify edit
    assert manager.lab_exists("Advanced Lab") is True
    assert manager.lab_exists("Test Lab") is False
    
    # Delete lab
    assert manager.delete_lab("Advanced Lab") is True
    assert manager.lab_exists("Advanced Lab") is False
    
    # Try to delete non-existent lab
    assert manager.delete_lab("Nonexistent Lab") is False


def test_lab_controller_basic_flow(tmp_path):
    """Test LabController basic operations."""
    manager = LabManager()
    controller = LabController(manager)

    # Add lab via controller (lab names are strings)
    assert controller.add_lab("Python Lab") is True
    
    # Check it exists
    labs = controller.get_labs()
    assert "Python Lab" in labs
    
    # Check lab existence via controller
    assert controller.lab_exists("Python Lab") is True
    
    # Lab controller doesn't have save_to_file method
    # Instead test that controller has expected functionality
    assert hasattr(controller, 'get_labs')
    assert hasattr(controller, 'lab_exists')


def test_lab_controller_modify_delete():
    """Test modifying and deleting labs through controller."""
    manager = LabManager()
    controller = LabController(manager)

    # Add initial lab (controller add_lab expects string name)
    lab_name = "Web Lab"

    controller.add_lab(lab_name)
    assert lab_name in controller.get_labs()
    
    # Edit lab (rename it)
    new_lab_name = "Updated Web Lab"
    assert controller.edit_lab(lab_name, new_lab_name) is True
    
    # Verify modification
    assert new_lab_name in controller.get_labs()
    assert lab_name not in controller.get_labs()
    
    # Delete lab
    assert controller.delete_lab(new_lab_name) is True
    assert new_lab_name not in controller.get_labs()


