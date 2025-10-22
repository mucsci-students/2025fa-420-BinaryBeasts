import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QDialogButtonBox,
    QMessageBox,
)
from scheduler.config import CombinedConfig, CourseConfig


BUTTON_STYLE = (
    "padding: 10px; background-color: #327f66; color: white; "
    "border-radius: 5px; width: 140px;"
)
TITLE_FONT = QFont("Arial", 19, QFont.Bold)
LABEL_FONT = QFont("Arial", 15)
BUTTON_FONT = QFont("Arial", 15)


class CourseDialog(QDialog):
    """
    Small form to add or edit a course section.
    Uses comma-separated text boxes for rooms, labs, etc.
    """

    def __init__(self, parent=None, course=None):
        super().__init__(parent)

        # Window
        self.setWindowTitle("Course Section")
        self.setModal(True)
        self.setMinimumWidth(520)

        # Title
        title_label = QLabel("Course Section")
        title_label.setFont(TITLE_FONT)
        title_label.setAlignment(Qt.AlignCenter)

        # form fields
        self.course_id_input = QLineEdit()
        self.credits_input = QSpinBox()
        self.credits_input.setRange(1, 12)

        self.rooms_input = QLineEdit()
        self.labs_input = QLineEdit()
        self.faculty_input = QLineEdit()
        self.conflicts_input = QLineEdit()

        # pre-fill when editing
        if course:
            self.course_id_input.setText(course.course_id)
            self.credits_input.setValue(course.credits)
            self.rooms_input.setText(", ".join(course.room))
            self.labs_input.setText(", ".join(course.lab))
            self.faculty_input.setText(", ".join(course.faculty))
            self.conflicts_input.setText(", ".join(course.conflicts))
        else:
            self.credits_input.setValue(4)

        form_layout = QFormLayout()
        form_layout.addRow("Course ID", self.course_id_input)
        form_layout.addRow("Credits", self.credits_input)
        form_layout.addRow("Rooms", self.rooms_input)
        form_layout.addRow("Labs", self.labs_input)
        form_layout.addRow("Faculty", self.faculty_input)
        form_layout.addRow("Conflicts", self.conflicts_input)

        tip = QLabel(
            "Tip: separate multiple values with commas (e.g. Roddy 140, Roddy 141)\n"
            "* Required: Course ID, Credits, at least one Room, at least one Faculty"
        )
        tip.setFont(QFont("Arial", 13))
        tip.setAlignment(Qt.AlignCenter)

        # Save / Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        for btn in button_box.buttons():
            btn.setFont(BUTTON_FONT)
            btn.setStyleSheet(BUTTON_STYLE)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # Layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(title_label)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(tip)
        main_layout.addWidget(button_box)

        self.result_course = None

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
        faculty_list = [
            s.strip() for s in self.faculty_input.text().split(",") if s.strip()
        ]
        conflict_list = [
            s.strip() for s in self.conflicts_input.text().split(",") if s.strip()
        ]

        if not room_list:
            QMessageBox.warning(self, "Error", "At least one room is required")
            return

        if not faculty_list:
            QMessageBox.warning(
                self, "Error", "At least one faculty member is required"
            )
            return

        self.result_course = {
            "course_id": course_id,
            "credits": credits,
            "room": room_list,
            "lab": lab_list,
            "faculty": faculty_list,
            "conflicts": conflict_list,
        }

        super().accept()


class CoursesDialog(QDialog):
    """
    Main window to manage all courses.
    Left: course IDs
    Right: sections of the selected course
    Buttons: Add / Edit / Delete / Save & Close / Cancel
    """

    def __init__(self, controller, combined_config, parent=None):
        super().__init__(parent)

        self.controller = controller
        self.combined_config = combined_config

        self.setWindowTitle("Scheduler")
        self.setMinimumWidth(950)
        self.setMinimumHeight(520)
        self.setModal(True)

        header = QLabel("Edit Courses")
        header.setFont(TITLE_FONT)
        header.setAlignment(Qt.AlignCenter)

        # left: course IDs
        self.course_id_list = QListWidget()
        self.course_id_list.setFont(LABEL_FONT)
        self.course_id_list.currentRowChanged.connect(self.show_sections)

        # right: sections
        self.section_list = QListWidget()
        self.section_list.setFont(LABEL_FONT)
        self.section_list.setWordWrap(True)

        self.add_button = QPushButton("Add")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        self.save_button = QPushButton("Save and Close")
        self.cancel_button = QPushButton("Cancel")

        for b in (
            self.add_button,
            self.edit_button,
            self.delete_button,
            self.save_button,
            self.cancel_button,
        ):
            b.setFont(BUTTON_FONT)
            b.setStyleSheet(BUTTON_STYLE)

        self.add_button.clicked.connect(self.add_section)
        self.edit_button.clicked.connect(self.edit_section)
        self.delete_button.clicked.connect(self.delete_section)
        self.save_button.clicked.connect(self.save_and_close)
        self.cancel_button.clicked.connect(self.reject)

        # layout: two columns, right side wider (3:1)
        lists_row = QHBoxLayout()

        left_box = QVBoxLayout()
        left_label = QLabel("Course IDs")
        left_label.setFont(LABEL_FONT)
        left_box.addWidget(left_label)
        left_box.addWidget(self.course_id_list)

        right_box = QVBoxLayout()
        right_label = QLabel("Sections")
        right_label.setFont(LABEL_FONT)
        right_box.addWidget(right_label)
        right_box.addWidget(self.section_list)

        lists_row.addLayout(left_box, 1)
        lists_row.addLayout(right_box, 3)

        # bottom button row
        button_row = QHBoxLayout()
        button_row.addWidget(self.add_button)
        button_row.addWidget(self.edit_button)
        button_row.addWidget(self.delete_button)
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.cancel_button)

        # layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(header)
        main_layout.addLayout(lists_row)
        main_layout.addLayout(button_row)

        # populate lists
        self.refresh_course_ids()

    def refresh_course_ids(self):
        """Updates the left list with course IDs, after adding/deleting courses"""
        self.course_id_list.clear()
        for course_id in sorted(self.controller.get_course_ids()):
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
        section_courses = self.controller.get_course(course_id)
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
        dialog = CourseDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            if dialog.result_course:
                self.controller.add_course(dialog.result_course)
                self.refresh_course_ids()

    def edit_section(self):
        item = self.section_list.currentItem()
        if not item:
            QMessageBox.information(
                self, "No section selected", "Please select a section to edit."
            )
            return
        course_id, section_index = item.data(Qt.UserRole)
        current_section = self.controller.get_course(course_id)[section_index]

        dialog = CourseDialog(self, course=current_section)
        if dialog.exec_() == QDialog.Accepted:
            updated_section = dialog.result_course
            if updated_section:
                if updated_section["course_id"] == course_id:
                    self.controller.modify_course(
                        course_id, section_index, updated_section
                    )
                else:
                    self.controller.delete_course(course_id, section_index)
                    self.controller.add_course(updated_section)
                self.refresh_course_ids()

    def delete_section(self):
        item = self.section_list.currentItem()
        if not item:
            QMessageBox.information(
                self, "No section selected", "Please select a section to continue."
            )
            return
        course_id, section_index = item.data(Qt.UserRole)
        confirm = QMessageBox.question(
            self, "Confirm", f"Delete {course_id} section {section_index + 1}?"
        )
        if confirm == QMessageBox.Yes:
            self.controller.delete_course(course_id, section_index)
            self.refresh_course_ids()

    def save_and_close(self):
        """Save changes."""
        try:
            if self.controller.save_to_combined_config(self.combined_config):
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to save")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
