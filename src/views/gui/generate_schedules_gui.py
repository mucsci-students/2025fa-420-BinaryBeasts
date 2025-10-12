import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
)
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QFileDialog
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import src.views.gui.main_gui as main_gui
from scheduler import Scheduler
from src.controllers import schedules_controller
#import main


class MainGUI(QWidget):

    def __init__(self, schedules_controller: schedules_controller):
        self.controller = schedules_controller
        super().__init__()
        self.init_ui()


    def init_ui(self):

        # Create the main layout
        layout = QVBoxLayout()


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
        """Return formatted text for the current schedule."""
        schedules = self.controller.schedules
        if not schedules:
            return "No schedules available."

        index = self.controller.index
        schedule = schedules[index]
        courses = [self._parse_course_csv(c.as_csv()) for c in schedule if c]
        if not courses:
            return "No course data in current schedule."
        lines = [
            f"📅 Schedule {index + 1} of {len(schedules)}",
            "-" * 90,
            f"{'Course':<12} | {'Faculty':<10} | {'MON':<12} | {'TUE':<12} | {'WED':<12} | {'THU':<12} | {'FRI':<12}",
            "-" * 90
        ]

        for course in courses:
            days = {'MON': '', 'TUE': '', 'WED': '', 'THU': '', 'FRI': ''}
            for slot in course['time_slots']:
                day_time = slot.replace('^', '').split(' ', 1)
                if len(day_time) == 2 and day_time[0] in days:
                    days[day_time[0]] += (('\n' if days[day_time[0]] else '') + day_time[1])
            lines.append(f"{course['course_id']:<12} | {course['faculty']:<10} | "
                         f"{days['MON']:<12} | {days['TUE']:<12} | {days['WED']:<12} | "
                         f"{days['THU']:<12} | {days['FRI']:<12}")
        return self.selected_label.setText("\n".join(lines))
    #self.selected_label.setText(sched[0])

    def save_schedule(self):
        folder_path = QFileDialog.getSaveFileName(self, "Select Directory", "config.json", "JSON Files (*.json)")[0]
        if folder_path:  
            pass

    def next_schedule(self):
        """Move to the next schedule and return its formatted text."""
        if not self.controller.schedules:
            return "No schedules available."
        self.controller.index = (self.controller.index + 1) % len(self.controller.schedules)
        self.selected_label.setText(self.get_current_schedule_text())

    def previous_schedule(self):
        """Move to the previous schedule and return its formatted text."""
        if not self.controller.schedules:
            return "No schedules available."
        self.controller.index = (self.controller.index - 1) % len(self.controller.schedules)
        self.selected_label.setText(self.get_current_schedule_text())

    def back(self):
        self.generate_schedule_window = main_gui.MainGUI()
        self.generate_schedule_window.show()
        self.close()

    def view_by_faculty(self):
        """Return a formatted view of the current schedule grouped by faculty."""
        schedules = self.controller.schedules
        if not schedules:
            return "No schedules available."

        index = self.controller.index
        schedule = schedules[index]
        courses = [self._parse_course_csv(c.as_csv()) for c in schedule if c]

        faculty_map = {}
        for course in courses:
            if course:
                faculty_map.setdefault(course['faculty'], []).append(course)

        if not faculty_map:
            return "No faculty data found in this schedule."

        lines = [f"👩‍🏫 Schedule {index + 1} - View by Faculty", "-" * 90]
        for faculty, items in sorted(faculty_map.items()):
            lines.append(f"\n👤 {faculty}")
            lines.append(f"{'Course':<12} | {'Room':<10} | {'Lab':<8} | {'MON':<12} | {'TUE':<12} | {'WED':<12} | {'THU':<12} | {'FRI':<12}")
            lines.append("-" * 90)
            for course in items:
                days = {'MON': '', 'TUE': '', 'WED': '', 'THU': '', 'FRI': ''}
                for slot in course['time_slots']:
                    slot = slot.replace('^', '')
                    parts = slot.split(' ', 1)
                    if len(parts) == 2 and parts[0] in days:
                        days[parts[0]] += (('\n' if days[parts[0]] else '') + parts[1])
                lab = course['lab'] if course['lab'].lower() != 'none' else '-'
                lines.append(f"{course['course_id']:<12} | {course['room']:<10} | {lab:<8} | "
                             f"{days['MON']:<12} | {days['TUE']:<12} | {days['WED']:<12} | "
                             f"{days['THU']:<12} | {days['FRI']:<12}")
        return self.selected_label.setText("\n".join(lines))

    def view_by_room(self):
        """Return a formatted view of the current schedule grouped by room and lab."""
        schedules = self.controller.schedules
        if not schedules:
            return "No schedules available."

        index = self.controller.index
        schedule = schedules[index]
        courses = [self._parse_course_csv(c.as_csv()) for c in schedule if c]

        room_map = {}
        lab_map = {}

        for course in courses:
            if course:
                room_map.setdefault(course['room'], []).append(course)
                if course['lab'] and course['lab'].lower() != 'none':
                    lab_map.setdefault(course['lab'], []).append(course)

        lines = [f"🏫 Schedule {index + 1} - View by Room", "-" * 90]

        for room, items in sorted(room_map.items()):
            lines.append(f"\n📍 Room: {room}")
            lines.append(f"{'Course':<12} | {'Faculty':<10} | {'MON':<12} | {'TUE':<12} | {'WED':<12} | {'THU':<12} | {'FRI':<12}")
            lines.append("-" * 90)
            for course in items:
                days = {'MON': '', 'TUE': '', 'WED': '', 'THU': '', 'FRI': ''}
                for slot in course['time_slots']:
                    slot = slot.replace('^', '')
                    parts = slot.split(' ', 1)
                    if len(parts) == 2 and parts[0] in days:
                        days[parts[0]] += (('\n' if days[parts[0]] else '') + parts[1])
                lines.append(f"{course['course_id']:<12} | {course['faculty']:<10} | "
                             f"{days['MON']:<12} | {days['TUE']:<12} | {days['WED']:<12} | "
                             f"{days['THU']:<12} | {days['FRI']:<12}")

        if lab_map:
            lines.append(f"\n🧪 Lab Sessions")
            lines.append("-" * 90)
            for lab, items in sorted(lab_map.items()):
                lines.append(f"\n🔬 Lab: {lab}")
                lines.append(f"{'Course':<12} | {'Faculty':<10} | {'MON':<12} | {'TUE':<12} | {'WED':<12} | {'THU':<12} | {'FRI':<12}")
                lines.append("-" * 90)
                for course in items:
                    days = {'MON': '', 'TUE': '', 'WED': '', 'THU': '', 'FRI': ''}
                    for slot in course['time_slots']:
                        if '^' in slot:
                            parts = slot.replace('^', '').split(' ', 1)
                            if len(parts) == 2 and parts[0] in days:
                                days[parts[0]] += (('\n' if days[parts[0]] else '') + parts[1])
                    lines.append(f"{course['course_id']:<12} | {course['faculty']:<10} | "
                                 f"{days['MON']:<12} | {days['TUE']:<12} | {days['WED']:<12} | "
                                 f"{days['THU']:<12} | {days['FRI']:<12}")
        self.selected_label.setText("\n".join(lines))

    def _parse_course_csv(self, course_csv: str) -> dict:
        parts = course_csv.strip().split(',')
        if len(parts) < 4:
            return None
        return {
            'course_id': parts[0].strip(),
            'faculty': parts[1].strip(),
            'room': parts[2].strip(),
            'lab': parts[3].strip(),
            'time_slots': [p.strip() for p in parts[4:]]
        }

if __name__ == "__main__":

    app = QApplication(sys.argv)
    gui = MainGUI()
    gui.show()
    sys.exit(app.exec_())

        




