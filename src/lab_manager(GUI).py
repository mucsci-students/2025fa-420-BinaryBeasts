# lab_manager_GUI.py
# Author: Naomi E.

"""
Interfaces with main file to implement a GUI for the add, modify, and delete lab 
feature functionality from the preexisting Scheduler CLI program.

User Story: Adding, Modifying, and Deleting Labs from a Scheduler Program (GUI)

"As a scheduler administrator, I want to press buttons that allow me to add, modify,
or delete preexisting labs from a course schedule builder (Scheduler)"

"""

# Import GUI widgets from PyQt5, json file configurations, etc.
import PyQt5.QtWidgets as qtw
import json

# Create GUI widget to contain Scheduler information
class LabManagerGUI(qtw.QWidget):
    def __init__(self, config_file):
        super().__init__()
        
        self.load_config(config_file)
        self.setWindowTitle("Lab Manager")
        # Set dimensions of GUI widget window for Scheduler
        self.setGeometry(200, 200, 600, 400)
        # Layout for application window
        self.layout = qtw.QVBoxLayout()
        
        self.title_label = qtw.QLabel("Add, Modify, or Delete Labs from Courses")
        self.layout.addWidget(self.title_label)
        
        # Display input course list from given JSON file via GUI
        self.course_list = qtw.QListWidget()
        self.update_course_list()
        self.layout.addWidget(self.course_list)
        
        # GUI Buttons to add, modify, and delete lab from course schedule
        self.add_button = qtw.QPushButton("Add Lab")
        self.modify_button = qtw.QPushButton("Modify Lab")
        self.delete_button = qtw.QPushButton("Delete Lab")
        
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.modify_button)
        self.layout.addWidget(self.delete_button)
        
    def load_config(self, config_file):    
        
    def add_lab(self):
        
    def mod_lab(self):
        
    def delete_lab(self):
        

        
        
app = qtw.QApplication([])