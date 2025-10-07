import sys
from PyQt5.QtWidgets import QApplication
from views.gui.generate_schedules_gui import MainGUI
from views.gui.main_gui import MainGUI


def main():
    app = QApplication(sys.argv)
    window = MainGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()