from PyQt5.QtWidgets import ( # type: ignore
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QLabel,
    QLineEdit,
    QDialogButtonBox,
    QMessageBox,
    QTabWidget,
    QWidget,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QGridLayout,
    QScrollArea,
    QFrame,
) # type: ignore
from PyQt5.QtCore import Qt # type: ignore
from PyQt5.QtGui import QFont # type: ignore

BUTTON_STYLE = (
    "padding: 10px; background-color: #327f66; color: white; "
    "border-radius: 5px; width: 140px;"
)
TITLE_FONT = QFont("Arial", 19, QFont.Bold)
LABEL_FONT = QFont("Arial", 15)
BUTTON_FONT = QFont("Arial", 15)
SMALL_FONT = QFont("Arial", 12)
SMALL_BUTTON_STYLE = (
    "padding: 6px; background-color: #327f66; color: white; "
    "border-radius: 4px; min-width: 70px;"
)

FRAME_STYLE = """
QFrame {
  background-color: palette(Base);
  border: 1px solid palette(Midlight);
  border-radius: 10px;
  padding: 12px;
}
"""


class DailyTimeSlotDialog(QDialog):
    """Dialog to add or edit a daily time slot."""

    def __init__(self, parent=None, day=None, slot_data=None):
        super().__init__(parent)

        self.setWindowTitle("Add Time Slot" if slot_data is None else "Edit Time Slot")
        self.setModal(True)
        self.setMinimumWidth(400)

        # Title
        title_label = QLabel("Add Time Slot" if slot_data is None else "Edit Time Slot")
        title_label.setFont(TITLE_FONT)
        title_label.setAlignment(Qt.AlignCenter) # type: ignore

        # Day selection
        self.day_combo = QComboBox()
        self.day_combo.addItems(["MON", "TUE", "WED", "THU", "FRI"])
        if day:
            self.day_combo.setCurrentText(day)
            self.day_combo.setEnabled(False)  # Don't allow changing day when editing

        # Start time input
        self.start_input = QLineEdit()
        self.start_input.setPlaceholderText("HH:MM (e.g., 08:00)")
        if slot_data and "start" in slot_data:
            self.start_input.setText(slot_data["start"])

        # End time input
        self.end_input = QLineEdit()
        self.end_input.setPlaceholderText("HH:MM (e.g., 17:00)")
        if slot_data and "end" in slot_data:
            self.end_input.setText(slot_data["end"])

        # Spacing input (optional)
        self.spacing_input = QSpinBox()
        self.spacing_input.setRange(1, 120)
        self.spacing_input.setValue(60)  # Default to 60 minutes
        self.spacing_input.setSuffix(" minutes")
        if slot_data and "spacing" in slot_data:
            self.spacing_input.setValue(slot_data["spacing"])

        # Form layout
        form_layout = QGridLayout()
        form_layout.addWidget(QLabel("Day:"), 0, 0)
        form_layout.addWidget(self.day_combo, 0, 1)
        form_layout.addWidget(QLabel("Start Time:"), 1, 0)
        form_layout.addWidget(self.start_input, 1, 1)
        form_layout.addWidget(QLabel("End Time:"), 2, 0)
        form_layout.addWidget(self.end_input, 2, 1)
        form_layout.addWidget(QLabel("Spacing:"), 3, 0)
        form_layout.addWidget(self.spacing_input, 3, 1)

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

        self.result_data = None

    def accept(self):
        """Called when Save is clicked."""
        start_time = self.start_input.text().strip()
        end_time = self.end_input.text().strip()
        
        if not start_time or not end_time:
            QMessageBox.warning(self, "Error", "Start and end times are required")
            return

        # Validate time format
        if not self._validate_time_format(start_time) or not self._validate_time_format(end_time):
            QMessageBox.warning(self, "Error", "Please use HH:MM format for times")
            return

        self.result_data = {
            "day": self.day_combo.currentText(),
            "start": start_time,
            "end": end_time,
            "spacing": self.spacing_input.value()
        }
        super().accept()

    def _validate_time_format(self, time_str: str) -> bool:
        """Validate time format (HH:MM)."""
        try:
            parts = time_str.split(":")
            if len(parts) != 2:
                return False
            
            hour = int(parts[0])
            minute = int(parts[1])
            
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except (ValueError, AttributeError):
            return False


class ClassPatternDialog(QDialog):
    """Dialog to add or edit a class pattern."""

    def __init__(self, parent=None, pattern_data=None):
        super().__init__(parent)

        self.setWindowTitle("Add Class Pattern" if pattern_data is None else "Edit Class Pattern")
        self.setModal(True)
        self.setMinimumWidth(500)

        # Title
        title_label = QLabel("Add Class Pattern" if pattern_data is None else "Edit Class Pattern")
        title_label.setFont(TITLE_FONT)
        title_label.setAlignment(Qt.AlignCenter) # type: ignore

        # Credits input
        self.credits_input = QSpinBox()
        self.credits_input.setRange(1, 8)
        self.credits_input.setValue(3)  # Default to 3 credits
        if pattern_data and "credits" in pattern_data:
            self.credits_input.setValue(pattern_data["credits"])

        # Start time input (optional)
        self.start_time_input = QLineEdit()
        self.start_time_input.setPlaceholderText("HH:MM (optional fixed start time)")
        if pattern_data and "start_time" in pattern_data:
            self.start_time_input.setText(pattern_data["start_time"])

        # Disabled checkbox
        self.disabled_checkbox = QCheckBox("Pattern is disabled")
        if pattern_data and pattern_data.get("disabled", False):
            self.disabled_checkbox.setChecked(True)

        # Meetings section
        meetings_label = QLabel("Meeting Schedule:")
        meetings_label.setFont(LABEL_FONT)

        # Container for meeting widgets
        self.meetings_container = QWidget()
        self.meetings_layout = QVBoxLayout(self.meetings_container)
        
        # Scroll area for meetings
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.meetings_container)
        scroll_area.setMaximumHeight(200)

        # Add meeting button
        self.add_meeting_button = QPushButton("Add Meeting")
        self.add_meeting_button.setStyleSheet(BUTTON_STYLE)
        self.add_meeting_button.clicked.connect(self.add_meeting)

        # Meeting widgets list
        self.meeting_widgets = []

        # Initialize with existing meetings or one default meeting
        if pattern_data and "meetings" in pattern_data:
            for meeting in pattern_data["meetings"]:
                self.add_meeting(meeting)
        else:
            self.add_meeting()  # Add one default meeting

        # Form layout
        form_layout = QGridLayout()
        form_layout.addWidget(QLabel("Credits:"), 0, 0)
        form_layout.addWidget(self.credits_input, 0, 1)
        form_layout.addWidget(QLabel("Start Time:"), 1, 0)
        form_layout.addWidget(self.start_time_input, 1, 1)
        form_layout.addWidget(self.disabled_checkbox, 2, 0, 1, 2)

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
        main_layout.addWidget(meetings_label)
        main_layout.addWidget(scroll_area)
        main_layout.addWidget(self.add_meeting_button)
        main_layout.addWidget(button_box)

        self.result_data = None

    def add_meeting(self, meeting_data=None):
        """Add a meeting widget."""
        meeting_widget = QFrame()
        meeting_widget.setStyleSheet(FRAME_STYLE)
        meeting_layout = QHBoxLayout(meeting_widget)

        # Day selection
        day_combo = QComboBox()
        day_combo.addItems(["MON", "TUE", "WED", "THU", "FRI"])
        if meeting_data and "day" in meeting_data:
            day_combo.setCurrentText(meeting_data["day"])

        # Duration input
        duration_input = QSpinBox()
        duration_input.setRange(30, 180)
        duration_input.setValue(50)  # Default to 50 minutes
        duration_input.setSuffix(" min")
        if meeting_data and "duration" in meeting_data:
            duration_input.setValue(meeting_data["duration"])

        # Lab checkbox
        lab_checkbox = QCheckBox("Lab session")
        if meeting_data and meeting_data.get("lab", False):
            lab_checkbox.setChecked(True)

        # Remove button
        remove_button = QPushButton("Remove")
        remove_button.setStyleSheet("padding: 5px; background-color: #d32f2f; color: white; border-radius: 3px;")
        remove_button.clicked.connect(lambda: self.remove_meeting(meeting_widget))

        meeting_layout.addWidget(QLabel("Day:"))
        meeting_layout.addWidget(day_combo)
        meeting_layout.addWidget(QLabel("Duration:"))
        meeting_layout.addWidget(duration_input)
        meeting_layout.addWidget(lab_checkbox)
        meeting_layout.addWidget(remove_button)

        self.meetings_layout.addWidget(meeting_widget)
        self.meeting_widgets.append({
            "widget": meeting_widget,
            "day_combo": day_combo,
            "duration_input": duration_input,
            "lab_checkbox": lab_checkbox
        })

    def remove_meeting(self, meeting_widget):
        """Remove a meeting widget."""
        if len(self.meeting_widgets) <= 1:
            QMessageBox.warning(self, "Error", "At least one meeting is required")
            return

        # Find and remove the widget
        for i, widget_data in enumerate(self.meeting_widgets):
            if widget_data["widget"] == meeting_widget:
                self.meetings_layout.removeWidget(meeting_widget)
                meeting_widget.deleteLater()
                self.meeting_widgets.pop(i)
                break

    def accept(self):
        """Called when Save is clicked."""
        if not self.meeting_widgets:
            QMessageBox.warning(self, "Error", "At least one meeting is required")
            return

        # Collect meeting data
        meetings = []
        for widget_data in self.meeting_widgets:
            meeting = {
                "day": widget_data["day_combo"].currentText(),
                "duration": widget_data["duration_input"].value(),
                "lab": widget_data["lab_checkbox"].isChecked()
            }
            meetings.append(meeting)

        # Validate start time format if provided
        start_time = self.start_time_input.text().strip()
        if start_time and not self._validate_time_format(start_time):
            QMessageBox.warning(self, "Error", "Please use HH:MM format for start time")
            return

        self.result_data = {
            "credits": self.credits_input.value(),
            "meetings": meetings,
            "disabled": self.disabled_checkbox.isChecked()
        }
        
        if start_time:
            self.result_data["start_time"] = start_time

        super().accept()

    def _validate_time_format(self, time_str: str) -> bool:
        """Validate time format (HH:MM)."""
        try:
            parts = time_str.split(":")
            if len(parts) != 2:
                return False
            
            hour = int(parts[0])
            minute = int(parts[1])
            
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except (ValueError, AttributeError):
            return False


class TimeSlotsDialog(QDialog):
    """Main dialog to manage time slot configuration."""

    def __init__(self, controller, combined_config, parent=None):
        super().__init__(parent)

        self.controller = controller
        self.combined_config = combined_config

        self.setWindowTitle("Scheduler - Time Slot Manager")
        self.setMinimumWidth(900)
        self.setMinimumHeight(600)
        self.setModal(True)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Header
        header = QLabel("Edit Time Slots")
        header.setFont(TITLE_FONT)
        header.setAlignment(Qt.AlignCenter) # type: ignore
        main_layout.addWidget(header)

        self.undo_button = QPushButton("Undo")
        self.redo_button = QPushButton("Redo")

        self.undo_button.setFont(QFont("Arial", 12))
        self.redo_button.setFont(QFont("Arial", 12))

        self.undo_button.setStyleSheet(SMALL_BUTTON_STYLE)
        self.redo_button.setStyleSheet(SMALL_BUTTON_STYLE)

        self.undo_button.clicked.connect(self.handle_undo)
        self.redo_button.clicked.connect(self.handle_redo)

        top_button_row = QHBoxLayout()
        top_button_row.addWidget(self.undo_button)
        top_button_row.addWidget(self.redo_button)
        top_button_row.addStretch()

        main_layout.addLayout(top_button_row)

        # Tab widget for daily times and class patterns
        self.tab_widget = QTabWidget()
        
        # Daily Times tab
        self.daily_times_tab = self._create_daily_times_tab()
        self.tab_widget.addTab(self.daily_times_tab, "Daily Time Slots")
        
        # Class Patterns tab
        self.class_patterns_tab = self._create_class_patterns_tab()
        self.tab_widget.addTab(self.class_patterns_tab, "Class Patterns")
        
        main_layout.addWidget(self.tab_widget)

        # Bottom buttons
        self.save_button = QPushButton("Save and Close")
        self.cancel_button = QPushButton("Cancel")

        for btn in (self.save_button, self.cancel_button):
            btn.setFont(BUTTON_FONT)
            btn.setStyleSheet(BUTTON_STYLE)

        self.save_button.clicked.connect(self.save_and_close)
        self.cancel_button.clicked.connect(self.reject)

        bottom_button_layout = QHBoxLayout()
        bottom_button_layout.addStretch()
        bottom_button_layout.addWidget(self.save_button)
        bottom_button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(bottom_button_layout)

        # Initialize data
        try:
            self.refresh_daily_times()
            self.refresh_class_patterns()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Initialization Error",
                f"Failed to initialize time slot manager: {str(e)}"
            )

    def _create_daily_times_tab(self):
        """Create the daily time slots tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Day selection
        day_layout = QHBoxLayout()
        day_layout.addWidget(QLabel("Day:"))
        self.day_combo = QComboBox()
        self.day_combo.addItems(["MON", "TUE", "WED", "THU", "FRI"])
        self.day_combo.currentTextChanged.connect(self.refresh_daily_times)
        day_layout.addWidget(self.day_combo)
        day_layout.addStretch()

        layout.addLayout(day_layout)

        # Time slots list
        self.daily_times_list = QListWidget()
        self.daily_times_list.setFont(LABEL_FONT)
        layout.addWidget(QLabel("Time Slots for Selected Day:"))
        layout.addWidget(self.daily_times_list)

        # Buttons for daily times
        daily_button_layout = QHBoxLayout()
        
        self.add_daily_button = QPushButton("Add Time Slot")
        self.edit_daily_button = QPushButton("Edit Time Slot")
        self.delete_daily_button = QPushButton("Delete Time Slot")
        self.show_spacing_button = QPushButton("Show Spacing")
        
        for btn in (self.add_daily_button, self.edit_daily_button, self.delete_daily_button, self.show_spacing_button):
            btn.setFont(BUTTON_FONT)
            btn.setStyleSheet(BUTTON_STYLE)
        
        self.add_daily_button.clicked.connect(self.add_daily_time_slot)
        self.edit_daily_button.clicked.connect(self.edit_daily_time_slot)
        self.delete_daily_button.clicked.connect(self.delete_daily_time_slot)
        self.show_spacing_button.clicked.connect(self.show_spacing_details)
        
        daily_button_layout.addWidget(self.add_daily_button)
        daily_button_layout.addWidget(self.edit_daily_button)
        daily_button_layout.addWidget(self.delete_daily_button)
        daily_button_layout.addWidget(self.show_spacing_button)
        daily_button_layout.addStretch()
        
        layout.addLayout(daily_button_layout)

        return tab

    def _create_class_patterns_tab(self):
        """Create the class patterns tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Class patterns list
        self.class_patterns_list = QListWidget()
        self.class_patterns_list.setFont(LABEL_FONT)
        layout.addWidget(QLabel("Class Meeting Patterns:"))
        layout.addWidget(self.class_patterns_list)

        # Buttons for class patterns
        patterns_button_layout = QHBoxLayout()
        
        self.add_pattern_button = QPushButton("Add Pattern")
        self.edit_pattern_button = QPushButton("Edit Pattern")
        self.delete_pattern_button = QPushButton("Delete Pattern")
        
        for btn in (self.add_pattern_button, self.edit_pattern_button, self.delete_pattern_button):
            btn.setFont(BUTTON_FONT)
            btn.setStyleSheet(BUTTON_STYLE)
        
        self.add_pattern_button.clicked.connect(self.add_class_pattern)
        self.edit_pattern_button.clicked.connect(self.edit_class_pattern)
        self.delete_pattern_button.clicked.connect(self.delete_class_pattern)
        
        patterns_button_layout.addWidget(self.add_pattern_button)
        patterns_button_layout.addWidget(self.edit_pattern_button)
        patterns_button_layout.addWidget(self.delete_pattern_button)
        patterns_button_layout.addStretch()
        
        layout.addLayout(patterns_button_layout)

        return tab

    def refresh_daily_times(self):
        """Update the daily time slots list."""
        self.daily_times_list.clear()
        try:
            current_day = self.day_combo.currentText()
            daily_times = self.controller.get_daily_times_for_day(current_day)
            
            for i, slot in enumerate(daily_times):
                spacing_text = f" (spacing: {slot['spacing']}min)" if slot.get('spacing') else ""
                slot_text = f"{slot['start']} - {slot['end']}{spacing_text}"
                self.daily_times_list.addItem(slot_text)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to refresh daily time slots: {str(e)}"
            )

    def refresh_class_patterns(self):
        """Update the class patterns list."""
        self.class_patterns_list.clear()
        try:
            patterns = self.controller.get_class_patterns()
            
            for i, pattern in enumerate(patterns):
                disabled_text = " [DISABLED]" if pattern.get("disabled", False) else ""
                credits = pattern.get("credits", 0)
                meetings_count = len(pattern.get("meetings", []))
                
                pattern_text = f"{credits} credits - {meetings_count} meetings{disabled_text}"
                
                # Add meeting details
                meetings_text = []
                for meeting in pattern.get("meetings", []):
                    lab_text = " (LAB)" if meeting.get("lab", False) else ""
                    meetings_text.append(f"{meeting['day']} {meeting['duration']}min{lab_text}")
                
                if meetings_text:
                    pattern_text += f" ({', '.join(meetings_text)})"
                
                self.class_patterns_list.addItem(pattern_text)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to refresh class patterns: {str(e)}"
            )

    def add_daily_time_slot(self):
        """Add a new daily time slot."""
        current_day = self.day_combo.currentText()
        dialog = DailyTimeSlotDialog(self, day=current_day)
        
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            try:
                data = dialog.result_data
                success = self.controller.add_daily_time_slot(
                    data["day"], data["start"], data["end"], data["spacing"]
                )
                
                if success:
                    QMessageBox.information(self, "Success", "Time slot added successfully.")
                    self.refresh_daily_times()
                else:
                    QMessageBox.warning(self, "Error", "Failed to add time slot (may conflict with existing slot).")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to add time slot: {str(e)}")

    def edit_daily_time_slot(self):
        """Edit the selected daily time slot."""
        current_row = self.daily_times_list.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Error", "Please select a time slot to edit.")
            return

        try:
            current_day = self.day_combo.currentText()
            daily_times = self.controller.get_daily_times_for_day(current_day)
            
            if current_row >= len(daily_times):
                QMessageBox.warning(self, "Error", "Invalid time slot selection.")
                return

            slot_data = daily_times[current_row]
            dialog = DailyTimeSlotDialog(self, day=current_day, slot_data=slot_data)
            
            if dialog.exec_() == QDialog.Accepted and dialog.result_data:
                data = dialog.result_data
                success = self.controller.update_daily_time_slot(
                    current_day, current_row, data["start"], data["end"], data["spacing"]
                )
                
                if success:
                    QMessageBox.information(self, "Success", "Time slot updated successfully.")
                    self.refresh_daily_times()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update time slot.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to edit time slot: {str(e)}")

    def delete_daily_time_slot(self):
        """Delete the selected daily time slot."""
        current_row = self.daily_times_list.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Error", "Please select a time slot to delete.")
            return

        try:
            current_day = self.day_combo.currentText()
            reply = QMessageBox.question(
                self, "Confirm Delete", 
                "Are you sure you want to delete this time slot?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success = self.controller.delete_daily_time_slot(current_day, current_row)
                
                if success:
                    QMessageBox.information(self, "Success", "Time slot deleted successfully.")
                    self.refresh_daily_times()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete time slot.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to delete time slot: {str(e)}")

    def add_class_pattern(self):
        """Add a new class pattern."""
        dialog = ClassPatternDialog(self)
        
        if dialog.exec_() == QDialog.Accepted and dialog.result_data:
            try:
                data = dialog.result_data
                success = self.controller.add_class_pattern(
                    data["credits"], 
                    data["meetings"], 
                    data["disabled"], 
                    data.get("start_time")
                )
                
                if success:
                    QMessageBox.information(self, "Success", "Class pattern added successfully.")
                    self.refresh_class_patterns()
                else:
                    QMessageBox.warning(self, "Error", "Failed to add class pattern.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to add class pattern: {str(e)}")

    def edit_class_pattern(self):
        """Edit the selected class pattern."""
        current_row = self.class_patterns_list.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Error", "Please select a class pattern to edit.")
            return

        try:
            patterns = self.controller.get_class_patterns()
            
            if current_row >= len(patterns):
                QMessageBox.warning(self, "Error", "Invalid class pattern selection.")
                return

            pattern_data = patterns[current_row]
            dialog = ClassPatternDialog(self, pattern_data=pattern_data)
            
            if dialog.exec_() == QDialog.Accepted and dialog.result_data:
                data = dialog.result_data
                success = self.controller.update_class_pattern(
                    current_row,
                    data["credits"], 
                    data["meetings"], 
                    data["disabled"], 
                    data.get("start_time")
                )
                
                if success:
                    QMessageBox.information(self, "Success", "Class pattern updated successfully.")
                    self.refresh_class_patterns()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update class pattern.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to edit class pattern: {str(e)}")

    def delete_class_pattern(self):
        """Delete the selected class pattern."""
        current_row = self.class_patterns_list.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Error", "Please select a class pattern to delete.")
            return

        try:
            reply = QMessageBox.question(
                self, "Confirm Delete", 
                "Are you sure you want to delete this class pattern?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                success = self.controller.delete_class_pattern(current_row)
                
                if success:
                    QMessageBox.information(self, "Success", "Class pattern deleted successfully.")
                    self.refresh_class_patterns()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete class pattern.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to delete class pattern: {str(e)}")

    def show_spacing_details(self):
        """Show all possible start times for the selected time slot."""
        current_row = self.daily_times_list.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Error", "Please select a time slot to view spacing details.")
            return

        try:
            current_day = self.day_combo.currentText()
            daily_times = self.controller.get_daily_times_for_day(current_day)
            
            if current_row < 0 or current_row >= len(daily_times):
                QMessageBox.warning(self, "Error", "Invalid time slot selection.")
                return
                
            slot = daily_times[current_row]
            start_time = slot["start"]
            end_time = slot["end"] 
            spacing = slot.get("spacing", 60)  # Default to 60 if no spacing
            
            # Calculate all possible start times
            start_times = self._calculate_possible_start_times(start_time, end_time, spacing)
            
            # Create and show the dialog
            self._show_spacing_dialog(current_day, slot, start_times)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to calculate spacing: {str(e)}")

    def _calculate_possible_start_times(self, start_time: str, end_time: str, spacing: int):
        """Calculate all possible start times given a time range and spacing."""
        def time_to_minutes(time_str):
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        
        def minutes_to_time(minutes):
            hours = minutes // 60
            mins = minutes % 60
            return f"{hours:02d}:{mins:02d}"
        
        start_minutes = time_to_minutes(start_time)
        end_minutes = time_to_minutes(end_time)
        
        start_times = []
        current = start_minutes
        
        while current <= end_minutes:
            start_times.append(minutes_to_time(current))
            current += spacing
            
        return start_times
    
    def _show_spacing_dialog(self, day: str, slot: dict, start_times: list):
        """Display a dialog showing the spacing details and possible start times."""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Spacing Details - {day}")
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout(dialog)
        
        # Header info
        header = QLabel(f"Time Slot Details for {day}")
        header.setFont(TITLE_FONT)
        header.setAlignment(Qt.AlignCenter)  # type: ignore[attr-defined]
        layout.addWidget(header)
        
        # Slot information
        info_layout = QGridLayout()
        info_layout.addWidget(QLabel("Start Time:"), 0, 0)
        info_layout.addWidget(QLabel(slot["start"]), 0, 1)
        info_layout.addWidget(QLabel("End Time:"), 1, 0)
        info_layout.addWidget(QLabel(slot["end"]), 1, 1)
        info_layout.addWidget(QLabel("Spacing:"), 2, 0)
        spacing_text = f"{slot.get('spacing', 60)} minutes"
        info_layout.addWidget(QLabel(spacing_text), 2, 1)
        
        info_frame = QFrame()
        info_frame.setLayout(info_layout)
        info_frame.setStyleSheet(FRAME_STYLE)
        layout.addWidget(info_frame)
        
        # Possible start times
        layout.addWidget(QLabel("Possible Class Start Times:"))
        
        # Create a scrollable list of start times
        times_list = QListWidget()
        times_list.setFont(LABEL_FONT)
        
        for i, start_time in enumerate(start_times):
            times_list.addItem(f"{start_time} (slot {i+1})")
            
        layout.addWidget(times_list)
        
        # Summary information
        summary_text = f"Total available slots: {len(start_times)}\n"
        summary_text += f"Time between slots: {slot.get('spacing', 60)} minutes\n"
        if len(start_times) > 1:
            summary_text += f"First slot: {start_times[0]} | Last slot: {start_times[-1]}"
        
        summary_label = QLabel(summary_text)
        summary_label.setStyleSheet("font-weight: bold; color: #327f66; padding: 10px;")
        summary_label.setAlignment(Qt.AlignCenter)  # type: ignore[attr-defined]
        layout.addWidget(summary_label)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.setFont(BUTTON_FONT)
        close_button.setStyleSheet(BUTTON_STYLE)
        close_button.clicked.connect(dialog.accept)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        dialog.exec_()

    def handle_undo(self):
        if self.controller.undo():
            self.refresh_daily_times()
            self.refresh_class_patterns()
        else:
            QMessageBox.information(self, "Undo", "Nothing to undo.")

    def handle_redo(self):
        if self.controller.redo():
            self.refresh_daily_times()
            self.refresh_class_patterns()
        else:
            QMessageBox.information(self, "Redo", "Nothing to redo.")

    def save_and_close(self):
        """Save changes and close the dialog."""
        try:
            # Save to combined config
            success = self.controller.save_to_combined_config(self.combined_config)
            
            if success:
                QMessageBox.information(
                    self,
                    "Success", 
                    "Time slot configuration saved successfully."
                )
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Warning",
                    "Some changes may not have been saved to the configuration."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save time slot configuration: {str(e)}"
            )