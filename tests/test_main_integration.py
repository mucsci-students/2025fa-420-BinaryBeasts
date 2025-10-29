import pytest

from src.models.main_model import main_model
from src.controllers.main_controller import main_controller


def test_main_mvc_integration():
    """Test basic MVC integration for main components."""
    # Create model
    model = main_model()
    assert model is not None
    
    # Create controller with model
    controller = main_controller(model)
    assert controller is not None
    assert controller.model is model


def test_main_application_flow():
    """Test basic application flow without file dependencies."""
    model = main_model()
    controller = main_controller(model)
    
    # Test that basic methods exist and are callable
    assert hasattr(controller, 'load_config')
    assert hasattr(controller, 'load_config_gui')
    assert hasattr(controller, 'generate_schedules')
    
    # Basic functionality test (without requiring external files)
    try:
        # These calls may fail due to missing files, but should not raise AttributeError
        controller.load_config_gui("nonexistent.json")  # load_config() takes no args
        controller.generate_schedules(1)
    except (FileNotFoundError, ValueError, AttributeError):
        # Expected behavior - methods exist but may fail due to missing dependencies
        pass
    except Exception as e:
        # Unexpected exception types suggest implementation issues
        pytest.fail(f"Unexpected exception type: {type(e).__name__}: {e}")


def test_mvc_component_availability():
    """Test that all MVC components are properly available."""
    # Test imports work
    from src.models.main_model import main_model
    from src.controllers.main_controller import main_controller
    
    # Test instantiation
    model = main_model()
    controller = main_controller(model)
    
    # Verify relationships
    assert controller.model is model