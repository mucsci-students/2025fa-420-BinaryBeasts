from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QLineEdit,
    QDialogButtonBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

BUTTON_STYLE = (
    "padding: 10px; background-color: #327f66; color: white; "
    "border-radius: 5px; width: 140px;"
)
TITLE_FONT = QFont('Arial', 19, QFont.Bold)
LABEL_FONT = QFont('Arial', 15)
BUTTON_FONT = QFont('Arial', 15)


class RoomDialog(QDialog):
    """Dialog to add or edit a single room."""

    def __init__(self, parent=None, room_name=None):
        super().__init__(parent)

        self.setWindowTitle("Add Room" if room_name is None else "Edit Room")
        self.setModal(True)
        self.setMinimumWidth(400)

        # Title
        title_label = QLabel("Add Room" if room_name is None else "Edit Room")
        title_label.setFont(TITLE_FONT)
        title_label.setAlignment(Qt.AlignCenter)

        # Room name input
        self.room_input = QLineEdit()
        self.room_input.setPlaceholderText("Enter room name (e.g., Roddy 147)")
        if room_name:
            self.room_input.setText(room_name)

        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Room Name:"))
        form_layout.addWidget(self.room_input)

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
        main_layout.addWidget(button_box)

        self.result_room = None

    def accept(self):
        """Called when Save is clicked."""
        room_name = self.room_input.text().strip()
        if not room_name:
            QMessageBox.warning(self, "Error", "Room name cannot be empty")
            return

        self.result_room = room_name
        super().accept()


class RoomsDialog(QDialog):
    """Main window to manage all rooms."""

    def __init__(self, controller, combined_config, parent=None):
        super().__init__(parent)

        self.controller = controller
        self.combined_config = combined_config

        self.setWindowTitle("Scheduler - Room Manager")
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)
        self.setModal(True)

        header = QLabel("Edit Rooms")
        header.setFont(TITLE_FONT)
        header.setAlignment(Qt.AlignCenter)

        # Room list
        self.room_list = QListWidget()
        self.room_list.setFont(LABEL_FONT)

        # Buttons
        self.add_button = QPushButton("Add Room")
        self.edit_button = QPushButton("Edit Room")
        self.delete_button = QPushButton("Delete Room")
        self.save_button = QPushButton("Save and Close")
        self.cancel_button = QPushButton("Cancel")

        for b in (self.add_button, self.edit_button, self.delete_button,
                  self.save_button, self.cancel_button):
            b.setFont(BUTTON_FONT)
            b.setStyleSheet(BUTTON_STYLE)

        self.add_button.clicked.connect(self.add_room)
        self.edit_button.clicked.connect(self.edit_room)
        self.delete_button.clicked.connect(self.delete_room)
        self.save_button.clicked.connect(self.save_and_close)
        self.cancel_button.clicked.connect(self.reject)

        # Layout
        list_layout = QVBoxLayout()
        list_label = QLabel("Rooms")
        list_label.setFont(LABEL_FONT)
        list_layout.addWidget(list_label)
        list_layout.addWidget(self.room_list)

        # Bottom button row
        button_row = QHBoxLayout()
        button_row.addWidget(self.add_button)
        button_row.addWidget(self.edit_button)
        button_row.addWidget(self.delete_button)
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.cancel_button)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(header)
        main_layout.addLayout(list_layout)
        main_layout.addLayout(button_row)

        # Populate list
        self.refresh_rooms()

    def refresh_rooms(self):
        """Update the room list."""
        self.room_list.clear()
        for room in sorted(self.controller.get_rooms()):
            self.room_list.addItem(room)

    def add_room(self):
        """Add a new room."""
        dialog = RoomDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            if dialog.result_room:
                success = self.controller.add_room(dialog.result_room)
                if success:
                    QMessageBox.information(self, "Success", f"Room '{dialog.result_room}' added successfully.")
                    self.refresh_rooms()
                else:
                    QMessageBox.warning(self, "Error", f"Room '{dialog.result_room}' already exists.")

    def edit_room(self):
        """Edit selected room."""
        item = self.room_list.currentItem()
        if not item:
            QMessageBox.information(self, "No room selected", "Please select a room to edit.")
            return

        old_name = item.text()
        dialog = RoomDialog(self, room_name=old_name)
        if dialog.exec_() == QDialog.Accepted:
            if dialog.result_room and dialog.result_room != old_name:
                success = self.controller.edit_room(old_name, dialog.result_room)
                if success:
                    # Update references in courses and faculty
                    try:
                        with self.combined_config.edit_mode() as editable_config:
                            # Update course room assignments
                            for course in editable_config.config.courses:
                                if hasattr(course, 'room') and isinstance(course.room, list):
                                    course.room = [dialog.result_room if r == old_name else r for r in course.room]

                            # Update faculty room preferences
                            for faculty in editable_config.config.faculty:
                                if hasattr(faculty, 'room_preferences') and isinstance(faculty.room_preferences, dict):
                                    if old_name in faculty.room_preferences:
                                        preference = faculty.room_preferences[old_name]
                                        del faculty.room_preferences[old_name]
                                        faculty.room_preferences[dialog.result_room] = preference
                    except Exception as e:
                        QMessageBox.warning(self, "Warning", f"Room renamed but failed to update references:\n{e}")

                    QMessageBox.information(self, "Success",
                        f"Room '{old_name}' renamed to '{dialog.result_room}'.\n"
                        "All course and faculty references have been updated.")
                    self.refresh_rooms()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to rename room. '{dialog.result_room}' may already exist.")

    def delete_room(self):
        """Delete selected room."""
        item = self.room_list.currentItem()
        if not item:
            QMessageBox.information(self, "No room selected", "Please select a room to delete.")
            return

        room_name = item.text()

        # Analyze impact
        affected_courses = []
        affected_faculty = []

        try:
            for course in self.combined_config.config.courses:
                if hasattr(course, 'room') and isinstance(course.room, list) and room_name in course.room:
                    affected_courses.append(course.course_id)

            for faculty in self.combined_config.config.faculty:
                if hasattr(faculty, 'room_preferences') and isinstance(faculty.room_preferences, dict):
                    if room_name in faculty.room_preferences:
                        affected_faculty.append(faculty.name)
        except Exception:
            pass

        # Build confirmation message
        impact_msg = f"Delete room '{room_name}'?\n\n"
        if affected_courses:
            impact_msg += f"This will remove the room from {len(affected_courses)} course(s):\n"
            impact_msg += ", ".join(affected_courses[:5])
            if len(affected_courses) > 5:
                impact_msg += f" and {len(affected_courses) - 5} more"
            impact_msg += "\n\n"
        if affected_faculty:
            impact_msg += f"This will remove room preferences from {len(affected_faculty)} faculty:\n"
            impact_msg += ", ".join(affected_faculty[:5])
            if len(affected_faculty) > 5:
                impact_msg += f" and {len(affected_faculty) - 5} more"
            impact_msg += "\n\n"

        confirm = QMessageBox.question(self, "Confirm Deletion", impact_msg)
        if confirm == QMessageBox.Yes:
            success = self.controller.delete_room(room_name)
            if success:
                # Remove references
                try:
                    with self.combined_config.edit_mode() as editable_config:
                        # Remove from courses
                        for course in editable_config.config.courses:
                            if hasattr(course, 'room') and isinstance(course.room, list):
                                if room_name in course.room:
                                    course.room = [r for r in course.room if r != room_name]

                        # Remove from faculty
                        for faculty in editable_config.config.faculty:
                            if hasattr(faculty, 'room_preferences') and isinstance(faculty.room_preferences, dict):
                                if room_name in faculty.room_preferences:
                                    del faculty.room_preferences[room_name]
                except Exception as e:
                    QMessageBox.warning(self, "Warning", f"Room deleted but failed to update references:\n{e}")

                QMessageBox.information(self, "Success", f"Room '{room_name}' deleted successfully.")
                self.refresh_rooms()
            else:
                QMessageBox.warning(self, "Error", f"Failed to delete room '{room_name}'.")

    def save_and_close(self):
        """Save changes and close."""
        try:
            if self.controller.save_to_combined_config(self.combined_config):
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to save")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")