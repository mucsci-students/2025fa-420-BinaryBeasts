import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
)
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QFileDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import src.views.gui.main_gui as main_gui
from scheduler import Scheduler
#import main


class MainGUI(QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):

        # Create the main layout
        layout = QVBoxLayout()

        #generate schedules
        #schedules = main.generate_schedules(main.config)

        self.setWindowTitle('College Course Scheduler')
        self.setMinimumWidth(800)
        #to keep track of which schedule is being displayed

        title = QLabel('College Course Scheduler')
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        RoomButton = QPushButton('View by Room')
        RoomButton.setFont(QFont('Arial', 8))
        RoomButton.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px;')
        layout.addWidget(RoomButton)
        RoomButton.clicked.connect(self.view_by_room)

        self.selected_label = QLabel()
        text = self.generate_schedules()
        self.selected_label.setFont(QFont('Arial', 10))
        self.selected_label.setText(text)
        self.selected_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.selected_label)


        SaveButton = QPushButton('Save Current Schedule')
        SaveButton.setFont(QFont('Arial', 8))
        SaveButton.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px;')
        layout.addWidget(SaveButton)
        SaveButton.clicked.connect(self.save_schedule)

        NextButton = QPushButton('Next Schedule')
        NextButton.setFont(QFont('Arial', 8))
        NextButton.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px;')
        layout.addWidget(NextButton)
        NextButton.clicked.connect(self.next_schedule)

        PreviousButton = QPushButton('Previous Schedule')
        PreviousButton.setFont(QFont('Arial', 8))
        PreviousButton.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px;')
        layout.addWidget(PreviousButton)
        PreviousButton.clicked.connect(self.previous_schedule)

        BackButton = QPushButton('Back to Main Menu')
        BackButton.setFont(QFont('Arial', 8))
        BackButton.setStyleSheet('padding: 10px; background-color: #f44336; color: white; border-radius: 5px;')
        layout.addWidget(BackButton)
        BackButton.clicked.connect(self.back)


        self.setLayout(layout)

    """"
    def generate_schedules(self):
        sched = main.next_schedule(num_schedules)
        self.selected_label.setText(sched)

    def save_schedule(self):
        folder_path = QFileDialog.getSaveFileName(self, "Select Directory", "config.json", "JSON Files (*.json)")[0]
        if folder_path:  
            print(folder_path)
            main.save_schedule(folder_path)

    def next_schedule(self):
        sched = main.next_schedule(num_schedules)
        self.selected_label.setText(sched)


    def previous_schedule(self):
        sched = main.previous_schedule(num_schedules)
        self.selected_label.setText(sched)

    def back(self):
        self.generate_schedule_window = main_gui.MainGUI()
        self.generate_schedule_window.show()
        self.close()

    def sort_by_room(self):
        # to be implemented
        print("Sorting by room not yet implemented.")

    def view_by_room(self):
        # to be implemented
        print("Viewing by room not yet implemented.")

"""
if __name__ == "__main__":

    app = QApplication(sys.argv)
    gui = MainGUI()
    gui.show()
    sys.exit(app.exec_())

        