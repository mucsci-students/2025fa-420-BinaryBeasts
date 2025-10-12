

import src.views.gui.roomGui as roomGui
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import src.views.gui.generate_schedules_gui as generate_schedules_gui
from PyQt5.QtWidgets import QInputDialog, QMessageBox
import src.views.gui.courses_gui as courses_gui
from src.controllers import schedules_controller
from src.controllers import main_controller

from scheduler import (
    Scheduler,
    load_config_from_file,
)
from scheduler.config import CombinedConfig

num_schedules = 0

class MainGUI(QWidget):
    file_uploaded = False


    def __init__(self, model, controller: main_controller):
        super().__init__()
        self.model = model
        self.controller = controller
        self.file_uploaded = False
        self.init_ui()


    def init_ui(self):
        self.setWindowTitle('College Course Sceduler')
        self.setMinimumWidth(800)
        self.setMinimumHeight(800)
        layout = QVBoxLayout()

        title = QLabel('College Course Scheduler')
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)


        CourseButton = QPushButton('Edit Courses')
        CourseButton.setFont(QFont('Arial', 8))
        CourseButton.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;')
        layout.addWidget(CourseButton)
        CourseButton.clicked.connect(self.open_course_manager)

        FacultyButton = QPushButton('Edit Faculty')
        FacultyButton .setFont(QFont('Arial', 8))
        FacultyButton .setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;')
        layout.addWidget(FacultyButton)
        FacultyButton .clicked.connect(self.open_faculty_manager)


        LabButton = QPushButton('Edit Labs')
        LabButton.setFont(QFont('Arial', 8))
        LabButton.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;')
        layout.addWidget(LabButton)
        LabButton.clicked.connect(self.open_lab_manager)

        RoomButton = QPushButton('Edit Rooms')
        RoomButton.setFont(QFont('Arial', 8))
        RoomButton.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;')
        layout.addWidget(RoomButton)
        RoomButton.clicked.connect(self.open_room_manager)

        SaveButton = QPushButton('Save Configuration File')
        SaveButton.setFont(QFont('Arial', 8))
        SaveButton.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;')
        layout.addWidget(SaveButton)
        SaveButton.clicked.connect(self.save_configuration)

        self.button = QPushButton('Upload Configuration File')
        self.button.setFont(QFont('Arial', 8))
        self.button.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;')
        layout.addWidget(self.button)
        self.button.clicked.connect(self.open_file_dialog)

        self.button = QPushButton('Upload Schedule')
        self.button.setFont(QFont('Arial', 8))
        self.button.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;')
        layout.addWidget(self.button)
        self.button.clicked.connect(self.load_schedule)

        GenerateButton = QPushButton('Generate Schedule')
        GenerateButton.setFont(QFont('Arial', 8))
        GenerateButton.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;')
        layout.addWidget(GenerateButton)
        GenerateButton.clicked.connect(self.generate_schedule)


        self.setLayout(layout)
    def open_file_dialog(self):
            file_path, _ = QFileDialog.getOpenFileName(self, 'Open JSON file', '', 'JSON Files (*.json)')
            if file_path:
                self.file_uploaded = True
                self.controller.load_config_gui(file_path)
                return

        
    def open_course_manager(self):
        if not self.file_uploaded:
            QMessageBox.critical(self, "Error", "Please upload a configuration file first.")
            return
        #self.course_window = courses_gui.CoursesDialog(self.config)
        #
        #self.course_window.show()

    def open_lab_manager(self):
        if not self.file_uploaded:
            QMessageBox.critical(self, "Error", "Please upload a configuration file first.")
            return
        print("Lab Manager Opened")

    def open_faculty_manager(self):
        if not self.file_uploaded:
            QMessageBox.critical(self, "Error", "Please upload a configuration file first.")
            return
        print("Faculty Manager Opened")
    
    def open_room_manager(self):
        if not self.file_uploaded:
            QMessageBox.critical(self, "Error", "Please upload a configuration file first.")
            return
        #try:
        #    self.room_window = roomGui.RoomGUI(self.config)
         #   self.room_window.show()
        #except Exception as e:
         #   QMessageBox.critical(self, "Error", f"Failed to open Room Manager:\n{e}")
       

    def save_configuration(self):
        if not self.file_uploaded:
            QMessageBox.critical(self, "Error", "Please upload a configuration file first.")
            return
        folder_path = QFileDialog.getSaveFileName(self, "Select Directory", "config.json", "JSON Files (*.json)")[0]

        if folder_path:  
            self.controller.save_config(folder_path)
        else:
            self.selected_label.setText('No folder selected.')

    def generate_schedule(self): 
        if not self.file_uploaded:
            QMessageBox.critical(self, "Error", "Please upload a configuration file first.")
            return       
        num, ok = QInputDialog.getInt(self, "Input Required", "Pick an amount of schedules to generate:", min=1)
        if not ok:
            return
        self.close()
        scheds = self.controller.generate_schedules(num)
        sched_controller = schedules_controller.generate_controller(scheds)
        self.generate_schedule_window = generate_schedules_gui.MainGUI(sched_controller)
        self.generate_schedule_window.show()
    
    def load_schedule(self):
        print("Schedule Loaded")

    def gen_sched(self):
        scheduler = Scheduler(self.config)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MainGUI()
    gui.show()
    sys.exit(app.exec_())




