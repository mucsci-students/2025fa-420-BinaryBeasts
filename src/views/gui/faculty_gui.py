from PyQt5.QtWidgets import ( # type : ignore
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QLabel,
    QLineEdit,
    QSpinBox,
    QPlainTextEdit,
    QDialogButtonBox,
    QMessageBox,
    QFormLayout,
) # type : ignore
from PyQt5.QtCore import Qt # type : ignore
from PyQt5.QtGui import QFont # type : ignore

BUTTON_STYLE = (
    "padding: 10px; background-color: #327f66; color: white; "
    "border-radius: 5px; width: 140px;"
)
TITLE_FONT = QFont("Arial", 19, QFont.Bold)
LABEL_FONT = QFont("Arial", 15)
BUTTON_FONT = QFont("Arial", 15)


class FacultyDialog(QDialog):
    """Dialog to add or edit a single faculty member."""

    def __init__(self, parent=None, faculty_data=None):
        super().__init__(parent)

        self.setWindowTitle("Add Faculty" if faculty_data is None else "Edit Faculty")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(700)

        # Title
        title_label = QLabel("Add Faculty" if faculty_data is None else "Edit Faculty")
        title_label.setFont(TITLE_FONT)
        title_label.setAlignment(Qt.AlignCenter) # type : ignore

        # Form inputs
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter faculty name (e.g., Dr. Smith)")
        form_layout.addRow("Name:", self.name_input)

        self.min_credits_input = QSpinBox()
        self.min_credits_input.setRange(0, 20)
        self.min_credits_input.setValue(0)
        form_layout.addRow("Minimum Credits:", self.min_credits_input)

        self.max_credits_input = QSpinBox()
        self.max_credits_input.setRange(0, 20)
        self.max_credits_input.setValue(9)
        form_layout.addRow("Maximum Credits:", self.max_credits_input)

        self.unique_limit_input = QSpinBox()
        self.unique_limit_input.setRange(1, 10)
        self.unique_limit_input.setValue(1)
        form_layout.addRow("Unique Course Limit:", self.unique_limit_input)

        # Times per day
        times_label = QLabel(
            "Availability (format: HH:MM-HH:MM, leave blank if not available):"
        )
        times_label.setFont(QFont("Arial", 12, QFont.Bold))

        self.time_inputs = {}
        days = ["MON", "TUE", "WED", "THU", "FRI"]
        for day in days:
            time_input = QLineEdit()
            time_input.setPlaceholderText("e.g., 09:00-17:00")
            form_layout.addRow(f"{day}:", time_input)
            self.time_inputs[day] = time_input

        # Preferences
        prefs_label = QLabel("Preferences (format: ItemName:Weight, one per line):")
        prefs_label.setFont(QFont("Arial", 12, QFont.Bold))

        self.course_prefs_input = QPlainTextEdit()
        self.course_prefs_input.setPlaceholderText("Example:\nCMSC 140:8\nCMSC 150:6")
        self.course_prefs_input.setMaximumHeight(80)

        self.room_prefs_input = QPlainTextEdit()
        self.room_prefs_input.setPlaceholderText("Example:\nRoddy 147:9\nRoddy 136:7")
        self.room_prefs_input.setMaximumHeight(80)

        self.lab_prefs_input = QPlainTextEdit()
        self.lab_prefs_input.setPlaceholderText("Example:\nMac:10\nLinux:5")
        self.lab_prefs_input.setMaximumHeight(80)

        # Load initial data if editing
        if faculty_data:
            self._load_faculty_data(faculty_data)

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
        main_layout.addWidget(times_label)
        main_layout.addWidget(prefs_label)
        main_layout.addWidget(QLabel("Course Preferences:"))
        main_layout.addWidget(self.course_prefs_input)
        main_layout.addWidget(QLabel("Room Preferences:"))
        main_layout.addWidget(self.room_prefs_input)
        main_layout.addWidget(QLabel("Lab Preferences:"))
        main_layout.addWidget(self.lab_prefs_input)
        main_layout.addWidget(button_box)

        self.result_faculty = None

    def _load_faculty_data(self, faculty):
        """Load existing faculty data into form."""
        self.name_input.setText(faculty.name)
        self.min_credits_input.setValue(faculty.minimum_credits)
        self.max_credits_input.setValue(faculty.maximum_credits)
        self.unique_limit_input.setValue(faculty.unique_course_limit)

        # Load times
        for day, time_input in self.time_inputs.items():
            if day in faculty.times and faculty.times[day]:
                try:
                    time_value = faculty.times[day]
                    
                    # Handle different time value formats
                    if isinstance(time_value, list) and time_value:
                        # If it's a list, take the first item
                        time_obj = time_value[0]
                    else:
                        # If it's a single value
                        time_obj = time_value
                    
                    # Convert TimeRange object to string format
                    if hasattr(time_obj, 'start') and hasattr(time_obj, 'end'):
                        # TimeRange object with start and end
                        time_str = f"{time_obj.start}-{time_obj.end}"
                    elif isinstance(time_obj, str):
                        # Already a string
                        time_str = time_obj
                    else:
                        # Convert to string as fallback
                        time_str = str(time_obj)
                    
                    time_input.setText(time_str)
                    
                except Exception as e:
                    # If any error occurs, just set empty string and continue
                    print(f"Warning: Could not load time for {day}: {e}")
                    time_input.setText("")

        # Load preferences
        if faculty.course_preferences:
            course_lines = [f"{k}:{v}" for k, v in faculty.course_preferences.items()]
            self.course_prefs_input.setPlainText("\n".join(course_lines))

        if faculty.room_preferences:
            room_lines = [f"{k}:{v}" for k, v in faculty.room_preferences.items()]
            self.room_prefs_input.setPlainText("\n".join(room_lines))

        if faculty.lab_preferences:
            lab_lines = [f"{k}:{v}" for k, v in faculty.lab_preferences.items()]
            self.lab_prefs_input.setPlainText("\n".join(lab_lines))

    def _parse_preferences(self, text_widget):
        """Parse preferences from text widget."""
        prefs = {}
        text = text_widget.toPlainText().strip()
        if not text:
            return prefs

        for line in text.splitlines():
            line = line.strip()
            if not line or ":" not in line:
                continue
            try:
                key, value = line.split(":", 1)
                prefs[key.strip()] = int(value.strip())
            except ValueError:
                continue
        return prefs

    def accept(self):
        """Called when Save is clicked."""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Faculty name cannot be empty")
            return

        min_credits = self.min_credits_input.value()
        max_credits = self.max_credits_input.value()

        if max_credits < min_credits:
            QMessageBox.warning(
                self, "Error", "Maximum credits cannot be less than minimum credits"
            )
            return

        # Parse times
        times = {}
        for day, time_input in self.time_inputs.items():
            time_str = time_input.text().strip()
            if time_str:
                times[day] = [time_str]
            else:
                times[day] = []

        # Parse preferences
        course_prefs = self._parse_preferences(self.course_prefs_input)
        room_prefs = self._parse_preferences(self.room_prefs_input)
        lab_prefs = self._parse_preferences(self.lab_prefs_input)

        self.result_faculty = {
            "name": name,
            "minimum_credits": min_credits,
            "maximum_credits": max_credits,
            "unique_course_limit": self.unique_limit_input.value(),
            "times": times,
            "course_preferences": course_prefs,
            "room_preferences": room_prefs,
            "lab_preferences": lab_prefs,
        }

        super().accept()


class FacultiesDialog(QDialog):
    """Main window to manage all faculty members."""

    def __init__(self, controller, combined_config, parent=None):
        super().__init__(parent)

        self.controller = controller
        self.combined_config = combined_config

        self.setWindowTitle("Scheduler - Faculty Manager")
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)
        self.setModal(True)

        header = QLabel("Edit Faculty")
        header.setFont(TITLE_FONT)
        header.setAlignment(Qt.AlignCenter) # type : ignore

        # Faculty list
        self.faculty_list = QListWidget()
        self.faculty_list.setFont(LABEL_FONT)

        # Buttons
        self.add_button = QPushButton("Add Faculty")
        self.edit_button = QPushButton("Edit Faculty")
        self.delete_button = QPushButton("Delete Faculty")
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

        self.add_button.clicked.connect(self.add_faculty)
        self.edit_button.clicked.connect(self.edit_faculty)
        self.delete_button.clicked.connect(self.delete_faculty)
        self.save_button.clicked.connect(self.save_and_close)
        self.cancel_button.clicked.connect(self.reject)

        # Layout
        list_layout = QVBoxLayout()
        list_label = QLabel("Faculty Members")
        list_label.setFont(LABEL_FONT)
        list_layout.addWidget(list_label)
        list_layout.addWidget(self.faculty_list)

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
        self.refresh_faculty()

    def refresh_faculty(self):
        """Update the faculty list."""
        self.faculty_list.clear()
        faculty_dict = self.controller.list_faculty()
        for name in sorted(faculty_dict.keys()):
            self.faculty_list.addItem(name)

    def add_faculty(self):
        """Add a new faculty member."""
        dialog = FacultyDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            if dialog.result_faculty:
                try:
                    success = self.controller.add_faculty(dialog.result_faculty)
                    if success:
                        QMessageBox.information(
                            self,
                            "Success",
                            f"Faculty '{dialog.result_faculty['name']}' added successfully.",
                        )
                        self.refresh_faculty()
                    else:
                        QMessageBox.warning(
                            self,
                            "Error",
                            f"Faculty '{dialog.result_faculty['name']}' already exists.",
                        )
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to add faculty:\n{e}")

    def edit_faculty(self):
        """Edit selected faculty member."""
        item = self.faculty_list.currentItem()
        if not item:
            QMessageBox.information(
                self, "No faculty selected", "Please select a faculty member to edit."
            )
            return

        name = item.text()
        faculty = self.controller.get_faculty(name)
        if not faculty:
            QMessageBox.warning(self, "Error", f"Faculty '{name}' not found.")
            return

        dialog = FacultyDialog(self, faculty_data=faculty)
        if dialog.exec_() == QDialog.Accepted:
            if dialog.result_faculty:
                try:
                    success = self.controller.modify_faculty(
                        name, dialog.result_faculty
                    )
                    if success:
                        QMessageBox.information(
                            self, "Success", f"Faculty '{name}' updated successfully."
                        )
                        self.refresh_faculty()
                    else:
                        QMessageBox.warning(
                            self,
                            "Error",
                            f"Failed to update faculty. New name '{dialog.result_faculty['name']}' may already exist.",
                        )
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to edit faculty:\n{e}")

    def delete_faculty(self):
        """Delete selected faculty member."""
        item = self.faculty_list.currentItem()
        if not item:
            QMessageBox.information(
                self, "No faculty selected", "Please select a faculty member to delete."
            )
            return

        name = item.text()

        # Analyze impact
        affected_courses = []
        try:
            for course in self.combined_config.config.courses:
                if (
                    hasattr(course, "faculty")
                    and isinstance(course.faculty, list)
                    and name in course.faculty
                ):
                    affected_courses.append(course.course_id)
        except Exception:
            pass

        # Build confirmation message
        impact_msg = f"Delete faculty '{name}'?\n\n"
        if affected_courses:
            impact_msg += f"This will remove the faculty from {len(affected_courses)} course(s):\n"
            impact_msg += ", ".join(affected_courses[:5])
            if len(affected_courses) > 5:
                impact_msg += f" and {len(affected_courses) - 5} more"
            impact_msg += "\n\n"

        confirm = QMessageBox.question(self, "Confirm Deletion", impact_msg)
        if confirm == QMessageBox.Yes:
            try:
                success = self.controller.delete_faculty(name)
                if success:
                    # Remove references from courses
                    try:
                        with self.combined_config.edit_mode() as editable_config:
                            for course in editable_config.config.courses:
                                if hasattr(course, "faculty") and isinstance(
                                    course.faculty, list
                                ):
                                    if name in course.faculty:
                                        course.faculty = [
                                            f for f in course.faculty if f != name
                                        ]
                    except Exception as e:
                        QMessageBox.warning(
                            self,
                            "Warning",
                            f"Faculty deleted but failed to update course references:\n{e}",
                        )

                    QMessageBox.information(
                        self, "Success", f"Faculty '{name}' deleted successfully."
                    )
                    self.refresh_faculty()
                else:
                    QMessageBox.warning(
                        self, "Error", f"Failed to delete faculty '{name}'."
                    )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete faculty:\n{e}")

    def save_and_close(self):
        """Save changes and close."""
        try:
            if self.controller.save_to_combined_config(self.combined_config):
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to save")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
