from PyQt5.QtWidgets import ( # type : ignore
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QLabel,
    QLineEdit,
    QDialogButtonBox,
    QMessageBox,
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


class LabDialog(QDialog):
    """Dialog to add or edit a single lab."""

    def __init__(self, parent=None, lab_name=None):
        super().__init__(parent)

        self.setWindowTitle("Add Lab" if lab_name is None else "Edit Lab")
        self.setModal(True)
        self.setMinimumWidth(400)

        # Title
        title_label = QLabel("Add Lab" if lab_name is None else "Edit Lab")
        title_label.setFont(TITLE_FONT)
        title_label.setAlignment(Qt.AlignCenter)

        # Lab name input
        self.lab_input = QLineEdit()
        self.lab_input.setPlaceholderText("Enter lab name (e.g., Mac, Linux, Windows)")
        if lab_name:
            self.lab_input.setText(lab_name)

        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Lab Name:"))
        form_layout.addWidget(self.lab_input)

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

        self.result_lab = None

    def accept(self):
        """Called when Save is clicked."""
        lab_name = self.lab_input.text().strip()
        if not lab_name:
            QMessageBox.warning(self, "Error", "Lab name cannot be empty")
            return

        self.result_lab = lab_name
        super().accept()


class LabsDialog(QDialog):
    """Main window to manage all labs."""

    def __init__(self, controller, combined_config, parent=None):
        super().__init__(parent)

        self.controller = controller
        self.combined_config = combined_config

        self.setWindowTitle("Scheduler - Lab Manager")
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)
        self.setModal(True)

        header = QLabel("Edit Labs")
        header.setFont(TITLE_FONT)
        header.setAlignment(Qt.AlignCenter)

        # Lab list
        self.lab_list = QListWidget()
        self.lab_list.setFont(LABEL_FONT)

        # Buttons
        self.add_button = QPushButton("Add Lab")
        self.edit_button = QPushButton("Edit Lab")
        self.delete_button = QPushButton("Delete Lab")
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

        self.add_button.clicked.connect(self.add_lab)
        self.edit_button.clicked.connect(self.edit_lab)
        self.delete_button.clicked.connect(self.delete_lab)
        self.save_button.clicked.connect(self.save_and_close)
        self.cancel_button.clicked.connect(self.reject)

        # Layout
        list_layout = QVBoxLayout()
        list_label = QLabel("Labs")
        list_label.setFont(LABEL_FONT)
        list_layout.addWidget(list_label)
        list_layout.addWidget(self.lab_list)

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
        self.refresh_labs()

    def refresh_labs(self):
        """Update the lab list."""
        self.lab_list.clear()
        for lab in sorted(self.controller.get_labs()):
            self.lab_list.addItem(lab)

    def add_lab(self):
        """Add a new lab."""
        dialog = LabDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            if dialog.result_lab:
                try:
                    success = self.controller.add_lab(dialog.result_lab)
                    if success:
                        QMessageBox.information(
                            self,
                            "Success",
                            f"Lab '{dialog.result_lab}' added successfully.",
                        )
                        self.refresh_labs()
                    else:
                        QMessageBox.warning(
                            self, "Error", f"Lab '{dialog.result_lab}' already exists."
                        )
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to add lab:\n{e}")

    def edit_lab(self):
        """Edit selected lab."""
        item = self.lab_list.currentItem()
        if not item:
            QMessageBox.information(
                self, "No lab selected", "Please select a lab to edit."
            )
            return

        old_name = item.text()
        dialog = LabDialog(self, lab_name=old_name)
        if dialog.exec_() == QDialog.Accepted:
            if dialog.result_lab and dialog.result_lab != old_name:
                try:
                    success = self.controller.edit_lab(old_name, dialog.result_lab)
                    if success:
                        # Update references in courses and faculty
                        try:
                            with self.combined_config.edit_mode() as editable_config:
                                # Update course lab assignments
                                for course in editable_config.config.courses:
                                    if hasattr(course, "lab") and isinstance(
                                        course.lab, list
                                    ):
                                        course.lab = [
                                            dialog.result_lab if lab == old_name else lab
                                            for lab in course.lab
                                        ]

                                # Update faculty lab preferences
                                for faculty in editable_config.config.faculty:
                                    if hasattr(
                                        faculty, "lab_preferences"
                                    ) and isinstance(faculty.lab_preferences, dict):
                                        if old_name in faculty.lab_preferences:
                                            preference = faculty.lab_preferences[
                                                old_name
                                            ]
                                            del faculty.lab_preferences[old_name]
                                            faculty.lab_preferences[
                                                dialog.result_lab
                                            ] = preference
                        except Exception as e:
                            QMessageBox.warning(
                                self,
                                "Warning",
                                f"Lab renamed but failed to update references:\n{e}",
                            )

                        QMessageBox.information(
                            self,
                            "Success",
                            f"Lab '{old_name}' renamed to '{dialog.result_lab}'.\n"
                            "All course and faculty references have been updated.",
                        )
                        self.refresh_labs()
                    else:
                        QMessageBox.warning(
                            self,
                            "Error",
                            f"Failed to rename lab. '{dialog.result_lab}' may already exist.",
                        )
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to edit lab:\n{e}")

    def delete_lab(self):
        """Delete selected lab."""
        item = self.lab_list.currentItem()
        if not item:
            QMessageBox.information(
                self, "No lab selected", "Please select a lab to delete."
            )
            return

        lab_name = item.text()

        # Analyze impact
        affected_courses = []
        affected_faculty = []

        try:
            for course in self.combined_config.config.courses:
                if (
                    hasattr(course, "lab")
                    and isinstance(course.lab, list)
                    and lab_name in course.lab
                ):
                    affected_courses.append(course.course_id)

            for faculty in self.combined_config.config.faculty:
                if hasattr(faculty, "lab_preferences") and isinstance(
                    faculty.lab_preferences, dict
                ):
                    if lab_name in faculty.lab_preferences:
                        affected_faculty.append(faculty.name)
        except Exception:
            pass

        # Build confirmation message
        impact_msg = f"Delete lab '{lab_name}'?\n\n"
        if affected_courses:
            impact_msg += (
                f"This will remove the lab from {len(affected_courses)} course(s):\n"
            )
            impact_msg += ", ".join(affected_courses[:5])
            if len(affected_courses) > 5:
                impact_msg += f" and {len(affected_courses) - 5} more"
            impact_msg += "\n\n"
        if affected_faculty:
            impact_msg += f"This will remove lab preferences from {len(affected_faculty)} faculty:\n"
            impact_msg += ", ".join(affected_faculty[:5])
            if len(affected_faculty) > 5:
                impact_msg += f" and {len(affected_faculty) - 5} more"
            impact_msg += "\n\n"

        confirm = QMessageBox.question(self, "Confirm Deletion", impact_msg)
        if confirm == QMessageBox.Yes:
            try:
                success = self.controller.delete_lab(lab_name)
                if success:
                    # Remove references
                    try:
                        with self.combined_config.edit_mode() as editable_config:
                            # Remove from courses
                            for course in editable_config.config.courses:
                                if hasattr(course, "lab") and isinstance(
                                    course.lab, list
                                ):
                                    if lab_name in course.lab:
                                        course.lab = [
                                            lab for lab in course.lab if lab != lab_name
                                        ]

                            # Remove from faculty
                            for faculty in editable_config.config.faculty:
                                if hasattr(faculty, "lab_preferences") and isinstance(
                                    faculty.lab_preferences, dict
                                ):
                                    if lab_name in faculty.lab_preferences:
                                        del faculty.lab_preferences[lab_name]
                    except Exception as e:
                        QMessageBox.warning(
                            self,
                            "Warning",
                            f"Lab deleted but failed to update references:\n{e}",
                        )

                    QMessageBox.information(
                        self, "Success", f"Lab '{lab_name}' deleted successfully."
                    )
                    self.refresh_labs()
                else:
                    QMessageBox.warning(
                        self, "Error", f"Failed to delete lab '{lab_name}'."
                    )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete lab:\n{e}")

    def save_and_close(self):
        """Save changes and close."""
        try:
            if self.controller.save_to_combined_config(self.combined_config):
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to save")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {str(e)}")
