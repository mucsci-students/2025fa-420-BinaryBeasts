import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
)
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QFileDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import src.views.gui.main_gui as main_gui
from scheduler import Scheduler
from src.controllers.schedules_controller import generate_controller


class SchedulesGUI(QWidget):

    def __init__(self, schedules=None, config=None):
        super().__init__()
        self.schedules = schedules if schedules else []
        self.config = config
        # Use the schedules_controller for navigation and saving logic
        self.controller = generate_controller(self.schedules)
        # Room view state
        self.viewing_by_room = False
        self.room_list = []
        self.current_room_index = 0
        self.room_schedule_data = {}
        self.init_ui()

    def init_ui(self):

        # Create the main layout
        self.layout = QVBoxLayout()

        self.setWindowTitle('College Course Scheduler - Schedules')
        self.setMinimumWidth(800)

        self.title = QLabel('Schedule Viewer')
        self.title.setFont(QFont('Arial', 16, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

        # View by Room button
        self.RoomButton = QPushButton('View by Room')
        self.RoomButton.setFont(QFont('Arial', 8))
        self.RoomButton.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px;')
        self.layout.addWidget(self.RoomButton)
        self.RoomButton.clicked.connect(self.view_by_room)

        # Display label
        self.selected_label = QLabel()
        text = self.generate_schedules()
        self.selected_label.setFont(QFont('Courier', 9))  # Monospace font for better alignment
        self.selected_label.setText(text)
        self.selected_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.layout.addWidget(self.selected_label)

        # Save button
        self.SaveButton = QPushButton('Save Current Schedule')
        self.SaveButton.setFont(QFont('Arial', 8))
        self.SaveButton.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px;')
        self.layout.addWidget(self.SaveButton)
        self.SaveButton.clicked.connect(self.save_schedule)

        # Schedule navigation buttons
        self.NextButton = QPushButton('Next Schedule')
        self.NextButton.setFont(QFont('Arial', 8))
        self.NextButton.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px;')
        self.layout.addWidget(self.NextButton)
        self.NextButton.clicked.connect(self.next_schedule)

        self.PreviousButton = QPushButton('Previous Schedule')
        self.PreviousButton.setFont(QFont('Arial', 8))
        self.PreviousButton.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px;')
        self.layout.addWidget(self.PreviousButton)
        self.PreviousButton.clicked.connect(self.previous_schedule)

        # Room navigation buttons (hidden by default)
        self.NextRoomButton = QPushButton('Next Room')
        self.NextRoomButton.setFont(QFont('Arial', 8))
        self.NextRoomButton.setStyleSheet('padding: 10px; background-color: #2196F3; color: white; border-radius: 5px;')
        self.layout.addWidget(self.NextRoomButton)
        self.NextRoomButton.clicked.connect(self.next_room)
        self.NextRoomButton.hide()

        self.PreviousRoomButton = QPushButton('Previous Room')
        self.PreviousRoomButton.setFont(QFont('Arial', 8))
        self.PreviousRoomButton.setStyleSheet('padding: 10px; background-color: #2196F3; color: white; border-radius: 5px;')
        self.layout.addWidget(self.PreviousRoomButton)
        self.PreviousRoomButton.clicked.connect(self.previous_room)
        self.PreviousRoomButton.hide()

        # Back to schedule view button (hidden by default)
        self.BackToScheduleButton = QPushButton('Back to Schedule View')
        self.BackToScheduleButton.setFont(QFont('Arial', 8))
        self.BackToScheduleButton.setStyleSheet('padding: 10px; background-color: #FF9800; color: white; border-radius: 5px;')
        self.layout.addWidget(self.BackToScheduleButton)
        self.BackToScheduleButton.clicked.connect(self.back_to_schedule_view)
        self.BackToScheduleButton.hide()

        # Back to main menu button
        self.BackButton = QPushButton('Back to Main Menu')
        self.BackButton.setFont(QFont('Arial', 8))
        self.BackButton.setStyleSheet('padding: 10px; background-color: #f44336; color: white; border-radius: 5px;')
        self.layout.addWidget(self.BackButton)
        self.BackButton.clicked.connect(self.back)

        self.setLayout(self.layout)

    def generate_schedules(self):
        """Display the current schedule using controller's index in tabular format"""
        if not self.schedules:
            return "No schedules generated yet."

        # Use controller's index for consistency
        schedule = self.schedules[self.controller.index]

        # Parse all courses
        from src.views.cli.schedules_view import parse_course_string
        courses = []
        for course_obj in schedule:
            course = parse_course_string(course_obj.as_csv())
            if course:
                courses.append(course)

        # Build tabular display
        text = f"Schedule {self.controller.index + 1} of {len(self.schedules)}\n\n"
        text += "=" * 100 + "\n"

        # Header
        text += f"{'Course ID':<15} {'Faculty':<12} {'Room':<12} {'Lab':<10} {'Time Slots':<40}\n"
        text += "=" * 100 + "\n"

        # Rows
        for course in courses:
            course_id = course['course_id']
            faculty = course['faculty']
            room = course['room']
            lab = course['lab'] if course['lab'] != 'None' else '-'

            # Format all time slots - show all of them
            time_slots = ', '.join(course['time_slots'])

            text += f"{course_id:<15} {faculty:<12} {room:<12} {lab:<10} {time_slots:<40}\n"

        text += "=" * 100 + "\n"
        return text

    def save_schedule(self):
        """Save schedules to file using controller logic"""
        if not self.schedules:
            QMessageBox.warning(self, "No Schedules", "No schedules available to save.")
            return

        # Ask for file path and format
        file_dialog = QFileDialog()
        file_path, selected_filter = file_dialog.getSaveFileName(
            self,
            "Save Schedules",
            "schedules.json",
            "JSON Files (*.json);;CSV Files (*.csv)"
        )

        if file_path:
            try:
                # Determine format based on file extension or filter
                format_type = 'csv' if file_path.endswith('.csv') or 'CSV' in selected_filter else 'json'

                # Use controller's save method
                self.controller._save_schedules_to_file(file_path, format_type)
                QMessageBox.information(self, "Success", f"Schedules saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save schedules:\n{e}")

    def next_schedule(self):
        """Navigate to next schedule using controller logic"""
        if not self.schedules:
            QMessageBox.warning(self, "No Schedules", "No schedules available.")
            return

        # Use controller's navigation method
        self.controller.next_schedule()
        text = self.generate_schedules()
        self.selected_label.setText(text)

    def previous_schedule(self):
        """Navigate to previous schedule using controller logic"""
        if not self.schedules:
            QMessageBox.warning(self, "No Schedules", "No schedules available.")
            return

        # Use controller's navigation method
        self.controller.previous_schedule()
        text = self.generate_schedules()
        self.selected_label.setText(text)

    def back(self):
        """Return to main menu"""
        from src.views.gui.main_gui import MainGUI as MainMenuGUI
        self.main_menu_window = MainMenuGUI()
        self.main_menu_window.show()
        self.close()

    def view_by_room(self):
        """Enter room-by-room navigation mode"""
        if not self.schedules or not self.schedules[self.controller.index]:
            QMessageBox.warning(self, "No Schedule", "No schedule available to view.")
            return

        # Convert schedule objects to CSV strings
        current_schedule_strings = [course.as_csv() for course in self.schedules[self.controller.index] if course is not None]

        # Parse and group by room
        from src.views.cli.schedules_view import parse_course_string
        self.room_schedule_data = {}
        for course_str in current_schedule_strings:
            course = parse_course_string(course_str)
            if course:
                room = course['room']
                if room not in self.room_schedule_data:
                    self.room_schedule_data[room] = []
                self.room_schedule_data[room].append(course)

        # Set up room navigation
        self.room_list = sorted(self.room_schedule_data.keys())
        self.current_room_index = 0
        self.viewing_by_room = True

        # Update UI for room viewing mode
        self.RoomButton.hide()
        self.NextButton.hide()
        self.PreviousButton.hide()
        self.NextRoomButton.show()
        self.PreviousRoomButton.show()
        self.BackToScheduleButton.show()
        self.title.setText('Room View')

        # Display first room
        self.display_current_room()

    def display_current_room(self):
        """Display the current room's schedule in weekly grid format"""
        if not self.room_list:
            self.selected_label.setText("No rooms found in schedule.")
            return

        room = self.room_list[self.current_room_index]
        courses = self.room_schedule_data[room]

        # Build weekly grid display for current room
        text = f"Schedule {self.controller.index + 1} - Room {self.current_room_index + 1} of {len(self.room_list)}\n\n"
        text += f"{room}\n"
        text += "=" * 95 + "\n"

        # Header with days of the week
        text += f"| {'Course':<12} | {'Faculty':<10} | {'MON':<11} | {'TUE':<11} | {'WED':<11} | {'THU':<11} | {'FRI':<11} |\n"
        text += "=" * 95 + "\n"

        # Process each course and organize time slots by day
        for course in courses:
            course_id = course['course_id']
            faculty = course['faculty']

            # Parse time slots by day
            day_times = {'MON': '', 'TUE': '', 'WED': '', 'THU': '', 'FRI': ''}

            for slot in course['time_slots']:
                # Extract day and time (format: "MON 14:00-14:50" or "MON 14:00-14:50^")
                slot_clean = slot.replace('^', '')  # Remove lab indicator
                parts = slot_clean.split(' ', 1)
                if len(parts) == 2:
                    day = parts[0].strip()
                    time = parts[1].strip()
                    if day in day_times:
                        day_times[day] = time

            # Print course row
            text += f"| {course_id:<12} | {faculty:<10} | {day_times['MON']:<11} | {day_times['TUE']:<11} | {day_times['WED']:<11} | {day_times['THU']:<11} | {day_times['FRI']:<11} |\n"

        text += "=" * 95 + "\n"
        self.selected_label.setText(text)

    def next_room(self):
        """Navigate to next room"""
        if not self.room_list:
            return

        self.current_room_index = (self.current_room_index + 1) % len(self.room_list)
        self.display_current_room()

    def previous_room(self):
        """Navigate to previous room"""
        if not self.room_list:
            return

        self.current_room_index = (self.current_room_index - 1) % len(self.room_list)
        self.display_current_room()

    def back_to_schedule_view(self):
        """Return to normal schedule viewing mode"""
        self.viewing_by_room = False
        self.room_list = []
        self.room_schedule_data = {}
        self.current_room_index = 0

        # Update UI for schedule viewing mode
        self.RoomButton.show()
        self.NextButton.show()
        self.PreviousButton.show()
        self.NextRoomButton.hide()
        self.PreviousRoomButton.hide()
        self.BackToScheduleButton.hide()
        self.title.setText('Schedule Viewer')

        # Display schedule again
        text = self.generate_schedules()
        self.selected_label.setText(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = SchedulesGUI()
    gui.show()
    sys.exit(app.exec_())