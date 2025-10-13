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


class MainGUI(QWidget):

    def __init__(self, schedules=None, config=None):
        super().__init__()
        self.schedules = schedules if schedules else []
        self.config = config
        # Use the schedules_controller for navigation and saving logic
        self.controller = generate_controller(self.schedules)
        self.init_ui()

    def init_ui(self):

        # Create the main layout
        layout = QVBoxLayout()

        #generate schedules
        #schedules = main.generate_schedules(main.config)

        self.setWindowTitle('College Course Scheduler')
        self.setMinimumWidth(800)
        #to keep track of which schedule is being displayed

        title = QLabel('College Course Scheduler')
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        RoomButton = QPushButton('View by Room')
        RoomButton.setFont(QFont('Arial', 8))
        RoomButton.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px;')
        layout.addWidget(RoomButton)
        RoomButton.clicked.connect(self.view_by_room)

        self.selected_label = QLabel()
        text = self.generate_schedules()
        self.selected_label.setFont(QFont('Arial', 10))
        self.selected_label.setText(text)
        self.selected_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.selected_label)


        SaveButton = QPushButton('Save Current Schedule')
        SaveButton.setFont(QFont('Arial', 8))
        SaveButton.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px;')
        layout.addWidget(SaveButton)
        SaveButton.clicked.connect(self.save_schedule)

        NextButton = QPushButton('Next Schedule')
        NextButton.setFont(QFont('Arial', 8))
        NextButton.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px;')
        layout.addWidget(NextButton)
        NextButton.clicked.connect(self.next_schedule)

        PreviousButton = QPushButton('Previous Schedule')
        PreviousButton.setFont(QFont('Arial', 8))
        PreviousButton.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px;')
        layout.addWidget(PreviousButton)
        PreviousButton.clicked.connect(self.previous_schedule)

        BackButton = QPushButton('Back to Main Menu')
        BackButton.setFont(QFont('Arial', 8))
        BackButton.setStyleSheet('padding: 10px; background-color: #f44336; color: white; border-radius: 5px;')
        layout.addWidget(BackButton)
        BackButton.clicked.connect(self.back)


        self.setLayout(layout)

    def generate_schedules(self):
        """Display the current schedule using controller's index"""
        if not self.schedules:
            return "No schedules generated yet."

        # Use controller's index for consistency
        schedule = self.schedules[self.controller.index]
        text = f"Schedule {self.controller.index + 1} of {len(self.schedules)}\n\n"

        for course in schedule:
            text += f"{course.as_csv()}\n"

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
        """View schedule organized by room using schedules_view logic"""
        if not self.schedules or not self.schedules[self.controller.index]:
            QMessageBox.warning(self, "No Schedule", "No schedule available to view.")
            return

        # Use the same logic as schedules_view.display_schedule_by_room
        # Convert schedule objects to CSV strings
        current_schedule_strings = [course.as_csv() for course in self.schedules[self.controller.index] if course is not None]

        # Parse and group by room
        from src.views.cli.schedules_view import parse_course_string
        room_schedule = {}
        for course_str in current_schedule_strings:
            course = parse_course_string(course_str)
            if course:
                room = course['room']
                if room not in room_schedule:
                    room_schedule[room] = []
                room_schedule[room].append(course)

        # Build display text
        text = f"Schedule {self.controller.index + 1} - View by Room\n\n"
        for room in sorted(room_schedule.keys()):
            text += f"Room: {room}\n"
            text += "-" * 60 + "\n"
            for course in room_schedule[room]:
                text += f"  {course['course_id']} - {course['faculty']}\n"
                for slot in course['time_slots']:
                    text += f"    {slot}\n"
            text += "\n"

        self.selected_label.setText(text)
if __name__ == "__main__":

    app = QApplication(sys.argv)
    gui = MainGUI()
    gui.show()
    sys.exit(app.exec_())

        




