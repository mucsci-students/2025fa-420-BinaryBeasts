import sys
from PyQt5.QtWidgets import QApplication
from courses_gui import CoursesDialog
from scheduler.config import CombinedConfig
from scheduler import load_config_from_file


def main():
    """Test the courses dialog with a sample config file"""
    app = QApplication(sys.argv)

    try:
        combined_config = load_config_from_file(CombinedConfig, "test_config.json")
    except FileNotFoundError:
        print("Error: test_config.json not found!")
        print("Please create a test configuration file first.")
        return

    dialog = CoursesDialog(combined_config)
    result = dialog.exec_()

    if result:
        combined_config.save("test_config.json")
        print("Changes saved to test_config.json")
    else:
        print("Cancelled - no changes saved")


if __name__ == "__main__":
    main()
