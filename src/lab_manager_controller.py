# lab_manager(controller).py
# Author: Naomi Ermold

"""
Interfaces with main file to implement a GUI for the add, modify, and delete lab 
feature functionality from the preexisting Scheduler CLI program in MVC format.

User Story: Adding, Modifying, and Deleting Labs from a Scheduler Program (GUI)

"As a scheduler administrator, I want to press buttons that allow me to add, modify,
or delete preexisting labs from a course schedule builder (Scheduler)"

"""

from PyQt5.QtCore import Qt
from src.models.lab_model import LabModel
from src.views.lab_view_gui import LabManagerView

class LabController:
    def __init__(self, config_file):
        self.model = LabModel(config_file)
        self.view = LabManagerView()

        self.load_courses()
        self.load_labs()

        # Connect buttons
        self.view.add_btn.clicked.connect(self.handle_add)
        self.view.modify_btn.clicked.connect(self.handle_modify)
        self.view.delete_btn.clicked.connect(self.handle_delete)
        self.view.course_dropdown.currentIndexChanged.connect(self.load_labs)

        self.view.show()

    def load_courses(self):
        self.view.course_dropdown.clear()
        for course in self.model.get_courses():
            self.view.course_dropdown.addItem(course.get("course_id", "Unknown"))

    def load_labs(self):
        self.view.lab_dropdown.clear()
        course_id = self.view.course_dropdown.currentText()
        course = self.model.get_course_by_id(course_id)
        if course and 'lab' in course:
            for lab in course['lab']:
                self.view.lab_dropdown.addItem(lab)

    def handle_add(self):
        course_id = self.view.course_dropdown.currentText()
        lab_name = self.view.new_lab_input.text().strip()

        if not lab_name:
            self.view.show_message("Input Error", "Please enter a lab name.", error=True)
            return

        success, msg = self.model.add_lab_to_course(course_id, lab_name)
        if success:
            self.model.save_config()
            self.load_labs()
            self.view.show_message("Success", msg)
        else:
            self.view.show_message("Failed", msg, error=True)

    def handle_modify(self):
        course_id = self.view.course_dropdown.currentText()
        old_lab = self.view.lab_dropdown.currentText()
        new_lab = self.view.new_lab_input.text().strip()

        if not new_lab:
            self.view.show_message("Input Error", "Please enter new lab name.", error=True)
            return

        success, msg = self.model.modify_lab(course_id, old_lab, new_lab)
        if success:
            self.model.save_config()
            self.load_labs()
            self.view.show_message("Success", msg)
        else:
            self.view.show_message("Failed", msg, error=True)

    def handle_delete(self):
        course_id = self.view.course_dropdown.currentText()
        lab_name = self.view.lab_dropdown.currentText()

        success, msg = self.model.delete_lab(course_id, lab_name)
        if success:
            self.model.save_config()
            self.load_labs()
            self.view.show_message("Success", msg)
        else:
            self.view.show_message("Failed", msg, error=True)
