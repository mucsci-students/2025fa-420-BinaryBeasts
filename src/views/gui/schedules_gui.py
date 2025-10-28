import sys
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QScrollArea, QComboBox, QTableWidget,
                             QTableWidgetItem, QHeaderView, QApplication,
                             QFileDialog, QMessageBox)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
from src.controllers.schedules_controller import generate_controller

FONT = QFont("Arial", 13)
FONT2 = QFont("Arial", 14)
LABEL_FONT = QFont('Arial', 16, QFont.Bold)

TABLE_STYLE = """
               QTableWidget {
                   background-color: white;
                   gridline-color: #dcdcdc;
                   border: 1px solid #bbb;
                   font-size: 10px;
                   color: black;
               }
               QTableWidget::item {
                   padding: 6px;
                   color: black;
                   background-color: white;
               }
               QTableWidget::item:selected {
                   background-color: #e3f2fd;
                   color: black;
               }
               QHeaderView::section {
                   background-color: #f0f0f0;
                   color: #222;
                   padding: 8px;
                   border: 1px solid #ccc;
                   font-weight: bold;
                   font-size: 10px;
               }
           """


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
        # Faculty view state
        self.viewing_by_faculty = False
        self.faculty_list = []
        self.current_faculty_index = 0
        self.faculty_schedule_data = {}
        self.init_ui()

    def init_ui(self):

        #the main layout
        self.layout = QVBoxLayout()
        self.setWindowTitle('College Course Scheduler - Schedules')
        self.setMinimumWidth(900)
        self.setMinimumHeight(800)

        header_layout = QHBoxLayout()

        self.title = QLabel('Schedule Viewer')
        self.title.setFont(LABEL_FONT)
        self.title.setAlignment(Qt.AlignCenter)  # type: ignore[attr-defined]
        header_layout.addWidget(self.title)

        header_layout.addStretch(1)

        view_label = QLabel('View:')
        view_label.setFont(FONT2)
        header_layout.addWidget(view_label)

        self.view_selector = QComboBox()
        self.view_selector.addItems(['All Schedules', 'By Room', 'By Faculty'])
        self.view_selector.setFont(FONT)
        self.view_selector.setMinimumWidth(150)
        self.view_selector.currentTextChanged.connect(self.view_by)
        header_layout.addWidget(self.view_selector)

        self.layout.addLayout(header_layout)

        #navigate controls
        nav_layout = QHBoxLayout()
        nav_layout.addStretch(1)

        #previous button
        prev_btn = QPushButton('◀ Previous')
        prev_btn.setFont(FONT2)
        prev_btn.setStyleSheet('padding: 8px 12px; background-color: #327f66; color: white; border-radius: 5px;')
        prev_btn.clicked.connect(self.go_previous_schedule)
        nav_layout.addWidget(prev_btn)

        #dropdown
        self.jump_selector = QComboBox()
        self.jump_selector.setFont(FONT2)
        self.jump_selector.setMinimumWidth(200)
        self.jump_selector.currentIndexChanged.connect(self.jump_to)
        nav_layout.addWidget(self.jump_selector)

        #next button
        next_btn = QPushButton('Next ▶')
        next_btn.setFont(FONT2)
        next_btn.setStyleSheet('padding: 8px 12px; background-color: #327f66; color: white; border-radius: 5px;')
        next_btn.clicked.connect(self.go_next_schedule)
        nav_layout.addWidget(next_btn)

        nav_layout.addStretch(1)
        self.layout.addLayout(nav_layout)

        #schedule display
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(400)

        #create a container widget for the table
        self.display_container = QWidget()
        self.display_layout = QVBoxLayout(self.display_container)
        self.display_layout.setContentsMargins(10, 10, 10, 10)

        #this will hold our schedule table
        self.schedule_table = None
        self.generate_schedules()

        scroll_area.setWidget(self.display_container)
        self.layout.addWidget(scroll_area)

        #save/back buttons
        action_layout = QHBoxLayout()

        self.SaveButton = QPushButton('Save Current Schedule')
        self.SaveButton.setFont(FONT2)
        self.SaveButton.setStyleSheet(
            'padding: 12px 20px; background-color: #327f66; color: white; border-radius: 5px;')
        self.SaveButton.clicked.connect(self.save_schedule)
        action_layout.addWidget(self.SaveButton)

        action_layout.addStretch(1)

        self.BackButton = QPushButton('← Back to Main Menu')
        self.BackButton.setFont(FONT2)
        self.BackButton.setStyleSheet(
            'padding: 12px 20px; background-color: #f44336; color: white; border-radius: 5px;')
        self.BackButton.clicked.connect(self.back)
        action_layout.addWidget(self.BackButton)

        self.layout.addLayout(action_layout)
        self.setLayout(self.layout)

        self.fill_jump_selector()

    def view_by(self, view_text):
        """Handle view selector changes"""
        if view_text == 'All Schedules':
            self.back_to_schedule_view()
        elif view_text == 'By Room':
            self.view_by_room()
        elif view_text == 'By Faculty':
            self.view_by_faculty()
        self.fill_jump_selector()

    def fill_jump_selector(self):
        """fill in dropdown based on current view"""
        self.jump_selector.blockSignals(True)
        self.jump_selector.clear()

        view_text = self.view_selector.currentText()

        if view_text == 'All Schedules':
            if hasattr(self, 'schedules') and self.schedules:
                for i in range(len(self.schedules)):
                    self.jump_selector.addItem(f"Schedule {i + 1}")
                self.jump_selector.setCurrentIndex(self.controller.index)
        elif view_text == 'By Room':
            if hasattr(self, 'room_list') and self.room_list:
                for i, room in enumerate(self.room_list):
                    self.jump_selector.addItem(f"{i + 1}. {room}")
                self.jump_selector.setCurrentIndex(self.current_room_index)
        elif view_text == 'By Faculty':
            if hasattr(self, 'faculty_list') and self.faculty_list:
                for i, faculty in enumerate(self.faculty_list):
                    self.jump_selector.addItem(f"{i + 1}. {faculty}")
                self.jump_selector.setCurrentIndex(self.current_faculty_index)

        self.jump_selector.blockSignals(False)

    def generate_schedules(self):
        """Display the current schedule using controller's index in table format"""
        if not self.schedules:
            label = QLabel("No schedules generated yet.")
            label.setStyleSheet("color: #7f8c8d; font-size: 14px; padding: 20px;")
            label.setAlignment(Qt.AlignCenter)  # type: ignore[attr-defined]

            while self.display_layout.count():
                item = self.display_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            self.display_layout.addWidget(label)
            return

        schedule = self.schedules[self.controller.index]

        # Parse all courses
        from src.views.cli.schedules_view import parse_course_string, get_earliest_time

        courses = []
        for course_obj in schedule:
            course = parse_course_string(course_obj.as_csv())
            if course:
                courses.append(course)

        # Sort courses by earliest time slot
        courses_sorted = sorted(courses, key=get_earliest_time)

        title_text = f"Schedule {self.controller.index + 1} of {len(self.schedules)}"
        self.create_schedule_table(courses_sorted, title_text)

    def create_schedule_table(self, courses, title_text):
        """Create a table for schedule display"""
        # Clear existing table if any
        if self.schedule_table:
            self.display_layout.removeWidget(self.schedule_table)
            self.schedule_table.deleteLater()

        # Add title label
        title_label = QLabel(title_text)
        title_label.setFont(LABEL_FONT)
        title_label.setAlignment(Qt.AlignCenter)  # type: ignore[attr-defined]

        # Clear layout
        while self.display_layout.count():
            item = self.display_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.display_layout.addWidget(title_label)

        # Create table
        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(7)
        self.schedule_table.setHorizontalHeaderLabels(
            ['Course', 'Room/Faculty', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])

        self.schedule_table.setStyleSheet(TABLE_STYLE)

        self.schedule_table.setRowCount(len(courses))

        #populate table
        for row, course in enumerate(courses):

            if row % 2 == 0:
                row_color = QColor(255, 255, 255)  # White
            else:
                row_color = QColor(248, 248, 248)  # light gray

            # Course ID
            course_item = QTableWidgetItem(course['course_id'])
            course_item.setFont(FONT)
            course_item.setBackground(row_color)
            course_item.setForeground(QColor(0, 0, 0))  # Black
            self.schedule_table.setItem(row, 0, course_item)

            # room/faculty
            info_item = QTableWidgetItem(course.get('room', course.get('faculty', '')))
            info_item.setFont(FONT)
            info_item.setBackground(row_color)
            info_item.setForeground(QColor(0, 0, 0))  # Black
            self.schedule_table.setItem(row, 1, info_item)

            # days of the week
            day_times = {'MON': '', 'TUE': '', 'WED': '', 'THU': '', 'FRI': ''}

            for slot in course['time_slots']:
                slot_clean = slot.replace('^', '')
                parts = slot_clean.split(' ', 1)
                if len(parts) == 2:
                    day = parts[0].strip()
                    time = parts[1].strip()
                    if day in day_times:
                        day_times[day] = time

            # slots to table
            days = ['MON', 'TUE', 'WED', 'THU', 'FRI']
            for col, day in enumerate(days, start=2):
                time_item = QTableWidgetItem(day_times[day])
                time_item.setFont(FONT)
                time_item.setBackground(row_color)
                time_item.setForeground(QColor(0, 0, 0))  # Black text
                time_item.setTextAlignment(Qt.AlignCenter)  # type: ignore[attr-defined]
                self.schedule_table.setItem(row, col, time_item)

        # resize columns to content
        header = self.schedule_table.horizontalHeader()
        for i in range(7):
            if i < 2:
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            else:
                header.setSectionResizeMode(i, QHeaderView.Stretch)

        # set row height
        self.schedule_table.verticalHeader().setDefaultSectionSize(35)
        self.schedule_table.verticalHeader().hide()

        self.display_layout.addWidget(self.schedule_table)

    def save_schedule(self):
        """Save schedules to file using controller logic"""
        if not self.schedules:
            QMessageBox.warning(self, "No Schedules", "No schedules available to save.")
            return

        file_dialog = QFileDialog()
        file_path, selected_filter = file_dialog.getSaveFileName(
            self,
            "Save Schedules",
            "schedules.json",
            "JSON Files (*.json);;CSV Files (*.csv)",
        )

        if file_path:
            try:
                # Determine format based on file extension or filter
                format_type = (
                    "csv"
                    if file_path.endswith(".csv") or "CSV" in selected_filter
                    else "json"
                )

                # Use controller's save method
                self.controller.save_schedules(file_path, format_type)
                QMessageBox.information(
                    self, "Success", f"Schedules saved to {file_path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save schedules:\n{e}")

    def go_next_schedule(self):
        """Navigate to next schedule using controller logic"""
        view_text = self.view_selector.currentText()
        if view_text == 'All Schedules':
            self.next_schedule()
        elif view_text == 'By Room':
            self.next_room()
        elif view_text == 'By Faculty':
            self.next_faculty()
        self.fill_jump_selector()

    def go_previous_schedule(self):
        """Navigate to previous schedule using controller logic"""
        view_text = self.view_selector.currentText()
        if view_text == 'All Schedules':
            self.previous_schedule()
        elif view_text == 'By Room':
            self.previous_room()
        elif view_text == 'By Faculty':
            self.previous_faculty()
        self.fill_jump_selector()

    def previous_schedule(self):
        """Navigate to previous schedule using controller"""
        self.controller.previous_schedule()
        self.generate_schedules()

    def next_schedule(self):
        """Navigate to next schedule using controller"""
        self.controller.next_schedule()
        self.generate_schedules()

    def back(self):
        """Return to main menu"""
        from src.views.gui.main_gui import MainGUI as MainMenuGUI

        self.main_menu_window = MainMenuGUI()
        self.main_menu_window.show()
        self.close()

    def jump_to(self, index):
        """Jump to selected item"""
        if index < 0:
            return
        view_text = self.view_selector.currentText()
        if view_text == 'All Schedules':
            self.controller.index = index
            self.generate_schedules()
        elif view_text == 'By Room':
            self.current_room_index = index
            self.display_current_room()
        elif view_text == 'By Faculty':
            self.current_faculty_index = index
            self.display_current_faculty()

    def view_by_room(self):
        """Enter room-by-room navigation mode"""
        if not self.schedules or not self.schedules[self.controller.index]:
            QMessageBox.warning(self, "No Schedule", "No schedule available to view.")
            return

        # Convert schedule objects to CSV strings
        current_schedule_strings = [
            course.as_csv()
            for course in self.schedules[self.controller.index]
            if course is not None
        ]

        from src.views.cli.schedules_view import parse_course_string

        self.room_schedule_data = {}
        for course_str in current_schedule_strings:
            course = parse_course_string(course_str)
            if course:
                room = course["room"]
                if room not in self.room_schedule_data:
                    self.room_schedule_data[room] = []
                self.room_schedule_data[room].append(course)

        self.room_list = sorted(self.room_schedule_data.keys())
        self.current_room_index = 0
        self.viewing_by_room = True

        self.display_current_room()

    def display_current_room(self):
        """Display the current room's schedule in weekly grid format"""
        if not self.room_list:
            label = QLabel("No rooms found in schedule.")
            label.setStyleSheet("color: #7f8c8d; font-size: 14px; padding: 20px;")
            label.setAlignment(Qt.AlignCenter)  # type: ignore[attr-defined]

            while self.display_layout.count():
                item = self.display_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            self.display_layout.addWidget(label)
            return

        room = self.room_list[self.current_room_index]
        courses = self.room_schedule_data[room]

        # Sort courses by earliest time slot
        from src.views.cli.schedules_view import get_earliest_time
        courses_sorted = sorted(courses, key=get_earliest_time)

        title_text = f"Schedule {self.controller.index + 1} - Room {self.current_room_index + 1} of {len(self.room_list)}: {room}"

        # Add faculty info to courses for display
        for course in courses_sorted:
            course['room'] = course.get('faculty', '')

        self.create_schedule_table(courses_sorted, title_text)

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

    def view_by_faculty(self):
        """Enter faculty-by-faculty navigation mode"""
        if not self.schedules or not self.schedules[self.controller.index]:
            QMessageBox.warning(self, "No Schedule", "No schedule available to view.")
            return

        current_schedule_strings = [course.as_csv()
                                    for course in self.schedules[self.controller.index]
                                    if course is not None]
        from src.views.cli.schedules_view import parse_course_string

        self.faculty_schedule_data = {}
        for course_str in current_schedule_strings:
            course = parse_course_string(course_str)
            if course:
                faculty = course["faculty"]
                if faculty not in self.faculty_schedule_data:
                    self.faculty_schedule_data[faculty] = []
                self.faculty_schedule_data[faculty].append(course)

        self.faculty_list = sorted(self.faculty_schedule_data.keys())
        self.current_faculty_index = 0
        self.viewing_by_faculty = True

        self.display_current_faculty()

    def display_current_faculty(self):
        """Display the current faculty's schedule in weekly grid format"""
        if not self.faculty_list:
            label = QLabel("No faculty found in schedule.")
            label.setStyleSheet("color: #7f8c8d; font-size: 14px; padding: 20px;")
            label.setAlignment(Qt.AlignCenter)  # type: ignore[attr-defined]

            while self.display_layout.count():
                item = self.display_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            self.display_layout.addWidget(label)
            return

        faculty = self.faculty_list[self.current_faculty_index]
        courses = self.faculty_schedule_data[faculty]

        # Sort courses by earliest time slot
        from src.views.cli.schedules_view import get_earliest_time
        courses_sorted = sorted(courses, key=get_earliest_time)

        title_text = f"Schedule {self.controller.index + 1} - Faculty {self.current_faculty_index + 1} of {len(self.faculty_list)}: {faculty}"
        self.create_schedule_table(courses_sorted, title_text)

    def next_faculty(self):
        """Navigate to next faculty"""
        if not self.faculty_list:
            return

        self.current_faculty_index = (self.current_faculty_index + 1) % len(
            self.faculty_list
        )
        self.display_current_faculty()

    def previous_faculty(self):
        """Navigate to previous faculty"""
        if not self.faculty_list:
            return

        self.current_faculty_index = (self.current_faculty_index - 1) % len(
            self.faculty_list
        )
        self.display_current_faculty()

    def back_to_schedule_view(self):
        """Return to normal schedule viewing mode"""
        self.viewing_by_room = False
        self.room_list = []
        self.room_schedule_data = {}
        self.current_room_index = 0
        self.viewing_by_faculty = False
        self.faculty_list = []
        self.faculty_schedule_data = {}
        self.current_faculty_index = 0
        self.title.setText('Schedule Viewer')
        self.generate_schedules()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = SchedulesGUI()
    gui.show()
    sys.exit(app.exec_())