import sys
from PyQt5.QtWidgets import QApplication
from typing import Dict, List, Optional, Tuple
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QFormLayout, QLineEdit,
    QSpinBox, QDialogButtonBox, QMessageBox
)

# import your Course + CourseManager from your own file
from courses import Course, CourseManager


class CourseForm(QDialog):
    """
    Small form to add or edit a course section.
    Uses comma-separated text boxes for rooms, labs, etc.
    """

    def __init__(self, parent: QWidget = None, course: Optional[Course] = None):
        super().__init__(parent)

        self.setWindowTitle("Course Section")
        self.setModal(True)

        # --- form fields ---
        self.course_id_input = QLineEdit()
        self.credits_input = QSpinBox()
        self.credits_input.setRange(1, 12)

        self.rooms_input = QLineEdit()
        self.labs_input = QLineEdit()
        self.faculty_input = QLineEdit()
        self.conflicts_input = QLineEdit()

        # if editing an existing course section, pre-fill values
        if course:
            self.course_id_input.setText(course.course_id)
            self.credits_input.setValue(course.credits)
            self.rooms_input.setText(", ".join(course.room))
            self.labs_input.setText(", ".join(course.lab))
            self.faculty_input.setText(", ".join(course.faculty))
            self.conflicts_input.setText(", ".join(course.conflicts))
        else:
            self.credits_input.setValue(3)

        form_layout = QFormLayout()
        form_layout.addRow("Course ID", self.course_id_input)
        form_layout.addRow("Credits", self.credits_input)
        form_layout.addRow("Rooms", self.rooms_input)
        form_layout.addRow("Labs", self.labs_input)
        form_layout.addRow("Faculty", self.faculty_input)
        form_layout.addRow("Conflicts", self.conflicts_input)

        # Save / Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(QLabel("Tip: separate multiple values with commas"))
        layout.addWidget(button_box)

        self.result_course: Optional[Course] = None

    def accept(self):
        """Called when Save is clicked."""
        course_id = self.course_id_input.text().strip()
        if not course_id:
            QMessageBox.warning(self, "Error", "Course ID cannot be empty")
            return

        credits = int(self.credits_input.value())

        # turn comma text into lists
        room_list = [s.strip() for s in self.rooms_input.text().split(",") if s.strip()]
        lab_list = [s.strip() for s in self.labs_input.text().split(",") if s.strip()]
        faculty_list = [s.strip() for s in self.faculty_input.text().split(",") if s.strip()]
        conflict_list = [s.strip() for s in self.conflicts_input.text().split(",") if s.strip()]

        try:
            self.result_course = Course(
                course_id=course_id,
                credits=credits,
                room=room_list,
                lab=lab_list,
                faculty=faculty_list,
                conflicts=conflict_list
            )
        except Exception as error:
            QMessageBox.critical(self, "Error", str(error))
            return

        super().accept()


class CoursesDialog(QDialog):
    """
    Main window to manage all courses.
    Left: course IDs
    Right: sections of the selected course
    Buttons: Add / Edit / Delete / Save & Close / Cancel
    """

    def __init__(self, config: Dict, parent: QWidget = None):
        super().__init__(parent)

        self.setWindowTitle("Edit Courses")
        self.setModal(True)

        # copy the config dict
        self.config = config
        self.course_manager = CourseManager()
        self.course_manager.load_courses(config.get("courses", []))

        # left list: Course IDs
        self.course_id_list = QListWidget()
        self.course_id_list.currentRowChanged.connect(self.show_sections)

        # right list: Sections
        self.section_list = QListWidget()

        # buttons
        self.add_button = QPushButton("Add")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.save_button = QPushButton("Save and Close")
        self.cancel_button = QPushButton("Cancel")

        self.add_button.clicked.connect(self.add_section)
        self.edit_button.clicked.connect(self.edit_section)
        self.delete_button.clicked.connect(self.delete_section)
        self.save_button.clicked.connect(self.save_and_close)
        self.cancel_button.clicked.connect(self.reject)

        # layout
        lists_row = QHBoxLayout()
        left_box = QVBoxLayout()
        left_box.addWidget(QLabel("Course IDs"))
        left_box.addWidget(self.course_id_list)

        right_box = QVBoxLayout()
        right_box.addWidget(QLabel("Sections"))
        right_box.addWidget(self.section_list)

        lists_row.addLayout(left_box, 1)
        lists_row.addLayout(right_box, 2)

        button_row = QHBoxLayout()
        button_row.addWidget(self.add_button)
        button_row.addWidget(self.edit_button)
        button_row.addWidget(self.delete_button)
        button_row.addStretch(1)
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.cancel_button)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(lists_row)
        main_layout.addLayout(button_row)

        self.refresh_course_ids()

        self.resize(900, 450)

    def refresh_course_ids(self):
        """Updates the left list with course IDs, after adding/deleting courses"""
        self.course_id_list.clear()
        for course_id in sorted(self.course_manager.get_course_ids()):
            self.course_id_list.addItem(course_id)
        if self.course_id_list.count() > 0:
            self.course_id_list.setCurrentRow(0)
        else:
            self.section_list.clear()

    def show_sections(self, _row: int):
        """Fill the right list with sections of the selected course."""
        self.section_list.clear()
        item = self.course_id_list.currentItem()
        if not item:
            return
        course_id = item.text()
        section_courses = self.course_manager.get_course(course_id)
        for section_index, course in enumerate(section_courses):
            text = (
                f"Section {section_index + 1} | "
                f"Credits: {course.credits} | "
                f"Rooms: {', '.join(course.room) or '-'} | "
                f"Labs: {', '.join(course.lab) or '-'} | "
                f"Faculty: {', '.join(course.faculty) or '-'} | "
                f"Conflicts: {', '.join(course.conflicts) or '-'}"
            )
            list_item = QListWidgetItem(text)
            list_item.setData(Qt.UserRole, (course_id, section_index))
            self.section_list.addItem(list_item)

    def add_section(self):
        dialog = CourseForm(self)
        if dialog.exec_() == QDialog.Accepted:
            if dialog.result_course:
                self.course_manager.add_course(dialog.result_course)
                self.refresh_course_ids()

    def edit_section(self):
        item = self.section_list.currentItem()
        if not item:
            return
        course_id, section_index = item.data(Qt.UserRole)
        current_section = self.course_manager.get_course(course_id)[section_index]

        dialog = CourseForm(self, course=current_section)
        if dialog.exec_() == QDialog.Accepted:
            updated_section = dialog.result_course
            if updated_section:
                if updated_section.course_id == course_id:
                    self.course_manager.modify_course(course_id, section_index, updated_section)
                else:
                    self.course_manager.delete_course(course_id, section_index)
                    self.course_manager.add_course(updated_section)
                self.refresh_course_ids()

    def delete_section(self):
        item = self.section_list.currentItem()
        if not item:
            return
        course_id, section_index = item.data(Qt.UserRole)
        confirm = QMessageBox.question(self, "Confirm", f"Delete {course_id} section {section_index+1}?")
        if confirm == QMessageBox.Yes:
            self.course_manager.delete_course(course_id, section_index)
            self.refresh_course_ids()

    def save_and_close(self):
        """Export back into config and close."""

        """Placeholder: will save later."""
        # for now, just close the dialog
        self.accept()

# quick test
if __name__ == "__main__":

    app = QApplication(sys.argv)

    fake_config = {
        "courses": [
            {"course_id": "CMSC 161", "credits": 4, "room": ["Roddy 140"], "lab": ["Mac"], "faculty": ["Dr. X"], "conflicts": []},
            {"course_id": "CMSC 161", "credits": 4, "room": ["Roddy 140"], "lab": ["Linux"], "faculty": ["Dr. Y"], "conflicts": []},
            {"course_id": "CMSC 162", "credits": 4, "room": ["Roddy 136"], "lab": [], "faculty": ["Dr. X"],"conflicts": ["CMCS 161"]},
            {"course_id": "CMSC 140", "credits": 4, "room": ["Roddy 141"], "lab": [], "faculty": ["Dr. Y"], "conflicts": []},

        ]
    }

    dialog = CoursesDialog(fake_config)          # create the dialog
    result = dialog.exec_()                      # run it modally
    if result:                                   # QDialog.Accepted is truthy
        print("Saved! Entries:", len(fake_config["courses"]))
        for course in fake_config["courses"]:
            print(course)
    else:
        print("Cancelled")
