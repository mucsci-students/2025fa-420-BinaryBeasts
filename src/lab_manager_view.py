# lab_manager(view).py
# Author: Naomi E.

"""
Interfaces with main file to implement a GUI for the add, modify, and delete lab 
feature functionality from the preexisting Scheduler CLI program in MVC format.

User Story: Adding, Modifying, and Deleting Labs from a Scheduler Program (GUI)

"As a scheduler administrator, I want to press buttons that allow me to add, modify,
or delete preexisting labs from a course schedule builder (Scheduler)"

"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QComboBox, QPushButton, QMessageBox, QLineEdit
)

class LabManagerView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lab Manager")
        self.setGeometry(300, 300, 400, 300)

        # Widgets
        self.course_dropdown = QComboBox()
        self.lab_dropdown = QComboBox()
        self.new_lab_input = QLineEdit()

        self.add_btn = QPushButton("Add Lab")
        self.modify_btn = QPushButton("Modify Lab")
        self.delete_btn = QPushButton("Delete Lab")

        # Layouts
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Select Course:"))
        layout.addWidget(self.course_dropdown)

        layout.addWidget(QLabel("Select Existing Lab (for Modify/Delete):"))
        layout.addWidget(self.lab_dropdown)

        layout.addWidget(QLabel("New Lab Name (for Add/Modify):"))
        layout.addWidget(self.new_lab_input)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.modify_btn)
        btn_layout.addWidget(self.delete_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def show_message(self, title, text, error=False):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(QMessageBox.Warning if error else QMessageBox.Information)
        msg.exec_()
