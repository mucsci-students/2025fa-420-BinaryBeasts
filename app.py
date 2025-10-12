from src.models import main_model
import src.controllers.main_controller as main_controller
import src.views.cli.main_view as main_view
from src.views.gui import main_gui as MainGUI
from PyQt5.QtWidgets import QApplication
import sys
from scheduler import (
    Scheduler,
    load_config_from_file,
)
from scheduler import CombinedConfig
import json

def start_gui(model, controller):
    app = QApplication(sys.argv)
    window = MainGUI.MainGUI(model, controller)
    window.show()
    sys.exit(app.exec_())

def main():
    
    model = main_model.main_model()  
    controller = main_controller.main_controller(model)
    
    while True:
        input_str = input("Please enter gui or cli: ").strip().lower()
        if input_str == "gui":
            start_gui(model, controller)
            break
        elif input_str == "cli":
            controller.load_config()
            while True:
                input_str = main_view.get_user_input()
                if input_str.lower() in ("exit", "quit"):
                    break
                controller.process_input(input_str)
        else:
            print("Please enter a valid input (gui or cli)")

if __name__ == "__main__":
    main()

