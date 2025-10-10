from src.models import main_model
import src.controllers.main_controller as main_controller
import src.views.cli.main_view as main_view
from src.views.gui import main_gui as MainGUI
from PyQt5.QtWidgets import QApplication
import sys


def main():
    model = main_model.main_model()
    controller = main_controller.main_controller(model)
    while(True):
        input_str = input("Please enter gui or cli: ")
        if(input_str == "gui"):
            app = QApplication(sys.argv)
            app = QApplication(sys.argv)
            window = MainGUI()
            window.show()
            sys.exit(app.exec_())
        elif(input_str == "cli"):
            controller.load_config()
            while True:
                input_str = main_view.get_user_input()
                controller.process_input(input_str)
        else: 
            print("Please enter a valid input")

main()