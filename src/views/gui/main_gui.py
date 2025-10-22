

import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QTabWidget, QHBoxLayout, QFileDialog,
    QHBoxLayout, QVBoxLayout, QStackedWidget, QLabel, QPushButton,
    QFrame, QGridLayout, QSizePolicy
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from src.views.gui.schedules_gui import SchedulesGUI
from PyQt5.QtWidgets import QInputDialog, QMessageBox
from src.views.gui.course_view_gui import CoursesDialog
from src.views.gui.roomGui import RoomsDialog
from src.views.gui.faculty_gui import FacultiesDialog
from src.views.gui.lab_gui import LabsDialog
from src.controllers.course_controller import CourseController
from src.controllers.room_controller import RoomController
from src.controllers.faculty_controller import FacultyController
from src.controllers.lab_controller import LabController
from src.models.course_model import CourseManager
from src.models.room_model import RoomManager
from src.models.faculty_model import FacultyManager
from src.models.lab_model import LabManager
import json

from scheduler import (
    Scheduler,
    load_config_from_file,
)
from scheduler.config import CombinedConfig

num_schedules = 0
TITLE_FONT = QFont("Arial", 18, QFont.Bold)
SECTION_FONT = QFont("Arial", 11, QFont.Bold)
LABEL_FONT = QFont("Arial", 10)
BUTTON_FONT = QFont("Arial", 10)

BUTTON_STYLE = """
    QPushButton {
        padding: 3px 6px;
        background-color: #327f66;
        color: white;
        border-radius: 6px;
        border: none;
        font-size: 10pt;
    }
    QPushButton:hover {
        background-color: #43A047;
    }
"""
PRIMARY_BUTTON_STYLE = """
    QPushButton {
        padding: 6px 10px;
        background-color: #327f66;
        color: white;
        border-radius: 6px;
        border: none;
        font-weight: bold;
        font-size: 13pt;
    }
    QPushButton:hover {
        background-color: #1D4ED8;
    }
"""

#TITLE_FONT = QFont("Arial", 18, QFont.Bold)
#SECTION_FONT = QFont("Arial", 14, QFont.Bold)
#LABEL_FONT = QFont("Arial", 13)
#BUTTON_FONT = QFont("Arial", 13)
#BUTTON_STYLE = ("padding: 8px 12px; background-color: #327f66; color: white; "
 #               "border-radius: 6px;")

class MainGUI(QWidget):
    file_uploaded = False

    def __init__(self):
        config = any

        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("College Course Scheduler")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header
        title = QLabel("College Course Scheduler")
        title.setFont(TITLE_FONT)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)



        # ===== Tab 2: Files =====
        files_tab = QWidget()
        files_layout = QVBoxLayout(files_tab)
        files_layout.setSpacing(10)

        files_label = QLabel("Files & Schedules")
        files_label.setFont(SECTION_FONT)
        files_layout.addWidget(files_label)

        self.selected_label = QLabel("No file selected")
        self.selected_label.setFont(LABEL_FONT)
        self.selected_label.setAlignment(Qt.AlignCenter)
        files_layout.addWidget(self.selected_label)

        upload_config_btn = QPushButton("Upload Configuration File");
        upload_config_btn.setFont(BUTTON_FONT);
        upload_config_btn.setStyleSheet(BUTTON_STYLE);
        upload_config_btn.clicked.connect(self.open_file_dialog)
        upload_schedule_btn = QPushButton("Upload Schedule");
        upload_schedule_btn.setFont(BUTTON_FONT);
        upload_schedule_btn.setStyleSheet(BUTTON_STYLE);
        upload_schedule_btn.clicked.connect(self.load_schedule)
        save_btn = QPushButton("Save Configuration File");
        save_btn.setFont(BUTTON_FONT);
        save_btn.setStyleSheet(BUTTON_STYLE);
        save_btn.clicked.connect(self.save_configuration)

        upload_config_btn.setMinimumHeight(24)
        upload_schedule_btn.setMinimumHeight(24)
        save_btn.setMinimumHeight(24)

        files_layout.addWidget(upload_config_btn)
        files_layout.addWidget(upload_schedule_btn)
        files_layout.addWidget(save_btn)
        files_layout.addStretch(1)
        tabs.addTab(files_tab, "Files")

        # ===== Tab 1: Data =====
        data_tab = QWidget()
        data_layout = QVBoxLayout(data_tab)
        data_layout.setSpacing(10)

        manage_label = QLabel("Manage Data")
        manage_label.setFont(SECTION_FONT)
        data_layout.addWidget(manage_label)

        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)
        data_layout.addLayout(grid)

        courses_btn = QPushButton("Edit Courses");
        courses_btn.setFont(BUTTON_FONT);
        courses_btn.setStyleSheet(BUTTON_STYLE);
        courses_btn.clicked.connect(self.open_course_manager)
        faculty_btn = QPushButton("Edit Faculty");
        faculty_btn.setFont(BUTTON_FONT);
        faculty_btn.setStyleSheet(BUTTON_STYLE);
        faculty_btn.clicked.connect(self.open_faculty_manager)
        labs_btn = QPushButton("Edit Labs");
        labs_btn.setFont(BUTTON_FONT);
        labs_btn.setStyleSheet(BUTTON_STYLE);
        labs_btn.clicked.connect(self.open_lab_manager)
        rooms_btn = QPushButton("Edit Rooms");
        rooms_btn.setFont(BUTTON_FONT);
        rooms_btn.setStyleSheet(BUTTON_STYLE);
        rooms_btn.clicked.connect(self.open_room_manager)

        courses_btn.setMinimumHeight(36)
        faculty_btn.setMinimumHeight(36)
        labs_btn.setMinimumHeight(36)
        rooms_btn.setMinimumHeight(36)

        grid.addWidget(courses_btn, 0, 0)
        grid.addWidget(faculty_btn, 0, 1)
        grid.addWidget(labs_btn, 1, 0)
        grid.addWidget(rooms_btn, 1, 1)

        data_layout.addStretch(1)
        tabs.addTab(data_tab, "Data")

        # ===== Tab 3: Generate =====
        generate_tab = QWidget()
        generate_layout = QVBoxLayout(generate_tab)
        generate_layout.setSpacing(10)

        gen_label = QLabel("Generate Schedule")
        gen_label.setFont(SECTION_FONT)
        gen_label.setAlignment(Qt.AlignLeft)
        generate_layout.addWidget(gen_label)

        # Primary action
        generate_btn = QPushButton("Generate Schedule")
        generate_btn.setFont(BUTTON_FONT)
        generate_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
        generate_btn.setMinimumHeight(44)
        generate_btn.clicked.connect(self.generate_schedule)
        generate_layout.addWidget(generate_btn)

        # (optional) a small row for status later
        status_row = QHBoxLayout()
        self.status_label = QLabel("")  # you can set messages like "Generated OK" or errors here
        self.status_label.setFont(LABEL_FONT)
        self.status_label.setAlignment(Qt.AlignLeft)
        status_row.addWidget(self.status_label)
        status_row.addStretch(1)
        generate_layout.addLayout(status_row)

        generate_layout.addStretch(1)
        tabs.addTab(generate_tab, "Generate")

        layout.addStretch(1)


        self.setLayout(layout)
    def open_file_dialog(self):
            file_path, _ = QFileDialog.getOpenFileName(self, 'Open JSON file', '', 'JSON Files (*.json)')
            if file_path:
                self.file_uploaded = True
                config_obj = load_config_from_file(CombinedConfig, file_path)
                self.config = config_obj
                self.selected_label.setText(f'Selected: {file_path}')
                return
            else:
                self.selected_label.setText('No file selected.')

        
    def open_course_manager(self):
        if not self.file_uploaded:
            QMessageBox.critical(self, "Error", "Please upload a configuration file first.")
            return

        try:

            course_manager = CourseManager()
            courses_data = []
            for course in self.config.config.courses:
                courses_data.append({
                    'course_id': course.course_id,
                    'credits': course.credits,
                    'room': list(course.room) if hasattr(course.room, '__iter__') else [course.room],
                    'lab': list(course.lab) if hasattr(course.lab, '__iter__') else [course.lab],
                    'faculty': list(course.faculty) if hasattr(course.faculty, '__iter__') else [course.faculty],
                    'conflicts': list(course.conflicts) if hasattr(course.conflicts, '__iter__') else [course.conflicts]
                })

            course_manager.load_courses(courses_data)

            # Create controller
            controller = CourseController(course_manager)

            # Open the courses dialog
            self.course_window = CoursesDialog(controller, self.config, self)
            self.course_window.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Course Manager:\n{e}")

    def open_lab_manager(self):
        if not self.file_uploaded:
            QMessageBox.critical(self, "Error", "Please upload a configuration file first.")
            return
        try:
            # Create LabManager and load labs from config
            lab_manager = LabManager(self.config)

            # Create controller
            controller = LabController(lab_manager)

            # Open the labs dialog
            self.lab_window = LabsDialog(controller, self.config, self)
            self.lab_window.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Lab Manager:\n{e}")

    def open_faculty_manager(self):
        if not self.file_uploaded:
            QMessageBox.critical(self, "Error", "Please upload a configuration file first.")
            return
        try:
            # Create FacultyManager and load faculty from config
            faculty_manager = FacultyManager()
            faculty_data = []
            for faculty in self.config.config.faculty:
                faculty_data.append({
                    'name': faculty.name,
                    'minimum_credits': faculty.minimum_credits,
                    'maximum_credits': faculty.maximum_credits,
                    'unique_course_limit': faculty.unique_course_limit,
                    'times': dict(faculty.times) if hasattr(faculty, 'times') else {},
                    'course_preferences': dict(faculty.course_preferences) if hasattr(faculty, 'course_preferences') else {},
                    'room_preferences': dict(faculty.room_preferences) if hasattr(faculty, 'room_preferences') else {},
                    'lab_preferences': dict(faculty.lab_preferences) if hasattr(faculty, 'lab_preferences') else {}
                })

            faculty_manager.load_faculty(faculty_data)

            # Create controller
            controller = FacultyController(faculty_manager)

            # Open the faculty dialog
            self.faculty_window = FacultiesDialog(controller, self.config, self)
            self.faculty_window.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Faculty Manager:\n{e}")

        print("Faculty Manager Opened")
    def open_room_manager(self):
        if not self.file_uploaded:
            QMessageBox.critical(self, "Error", "Please upload a configuration file first.")
            return
        try:
            # Create RoomManager and load rooms from config
            room_manager = RoomManager(self.config)

            # Create controller
            controller = RoomController(room_manager)

            # Open the rooms dialog
            self.room_window = RoomsDialog(controller, self.config, self)
            self.room_window.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Room Manager:\n{e}")
       

    def save_configuration(self):
        if not self.file_uploaded:
            QMessageBox.critical(self, "Error", "Please upload a configuration file first.")
            return
        folder_path = QFileDialog.getSaveFileName(self, "Select Directory", "config.json", "JSON Files (*.json)")[0]

        if folder_path:
            try:
                save_config(self.config, folder_path)
                QMessageBox.information(self, "Success", f"Configuration saved to {folder_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save configuration:\n{e}")
        else:
            self.selected_label.setText('No folder selected.')

    def generate_schedule(self):
        if not self.file_uploaded:
            QMessageBox.critical(self, "Error", "Please upload a configuration file first.")
            return
        num, ok = QInputDialog.getInt(self, "Input Required", "Pick an amount of schedules to generate:", min=1)
        if not ok:
            return

        try:
            # Generate schedules using the Scheduler
            scheduler = Scheduler(self.config)
            schedules = []
            for i, schedule in enumerate(scheduler.get_models()):
                schedules.append(schedule)
                if i + 1 >= num:
                    break

            if not schedules:
                QMessageBox.warning(self, "No Schedules", "No valid schedules could be generated.")
                return

            # Close current window and open schedule viewer with the generated schedules
            self.close()
            self.generate_schedule_window = SchedulesGUI(schedules=schedules, config=self.config)
            self.generate_schedule_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate schedules:\n{e}")
    
    def load_schedule(self):
        """Load a previously saved schedule from JSON or CSV file."""
        if not self.file_uploaded:
            QMessageBox.critical(self, "Error", "Please upload a configuration file first.")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Open Schedule File',
            '',
            'Schedule Files (*.json *.csv);;JSON Files (*.json);;CSV Files (*.csv)'
        )

        if not file_path:
            return

        try:
            # Parse the schedule file
            if file_path.endswith('.json'):
                schedules = self._load_schedule_from_json(file_path)
            elif file_path.endswith('.csv'):
                schedules = self._load_schedule_from_csv(file_path)
            else:
                QMessageBox.critical(self, "Error", "Unsupported file format. Please use JSON or CSV.")
                return

            if not schedules:
                QMessageBox.warning(self, "No Schedules", "No schedules found in the file.")
                return

            # Close current window and open schedule viewer
            self.close()
            self.generate_schedule_window = SchedulesGUI(schedules=schedules, config=self.config)
            self.generate_schedule_window.show()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load schedule:\n{e}")

    def _load_schedule_from_json(self, file_path):
        """Load schedules from JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)

        schedules = []

        # Handle two possible JSON formats:
        # 1. Array of objects with schedule_id and courses fields
        # 2. Simple array of arrays of course CSV strings
        for schedule_data in data:
            schedule = []

            # Format 1: Object with 'courses' field
            if isinstance(schedule_data, dict) and 'courses' in schedule_data:
                for course_csv in schedule_data['courses']:
                    schedule.append(self._create_course_from_csv(course_csv))
            # Format 2: Direct array of course CSV strings
            elif isinstance(schedule_data, list):
                for course_csv in schedule_data:
                    schedule.append(self._create_course_from_csv(course_csv))
            # Format 3: Single course CSV string
            elif isinstance(schedule_data, str):
                schedule.append(self._create_course_from_csv(schedule_data))

            if schedule:
                schedules.append(schedule)

        return schedules

    def _load_schedule_from_csv(self, file_path):
        """Load schedules from CSV file."""
        import csv

        schedules = []
        current_schedule = []

        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                # Empty row separates schedules
                if not row or all(cell.strip() == '' for cell in row):
                    if current_schedule:
                        schedules.append(current_schedule)
                        current_schedule = []
                    continue

                # Skip header rows
                if row[0].startswith('Schedule') or row[0].startswith('Course'):
                    continue

                # Reconstruct CSV format from row
                course_csv = ','.join(row)
                current_schedule.append(self._create_course_from_csv(course_csv))

        # Add last schedule if exists
        if current_schedule:
            schedules.append(current_schedule)

        return schedules

    def _create_course_from_csv(self, course_csv):
        """Create a simple course object from CSV string for display purposes."""
        class ScheduleCourse:
            def __init__(self, csv_string):
                self._csv = csv_string

            def as_csv(self):
                return self._csv

        return ScheduleCourse(course_csv)

    def gen_sched(self):
        scheduler = Scheduler(self.config)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MainGUI()
    gui.show()
    sys.exit(app.exec_())




def save_config(config, path: str):

        config = config
        courses = []
        mon = []
        tue = []
        wed = []
        thu = []
        fri = []
        classes = []
        faculty = []

        # Extract time slots per day with spacing where available
        for monday in config.time_slot_config.times.get("MON", []):
            mon.append({"start": monday.start, "spacing": getattr(monday, "spacing", None), "end": monday.end})
        for tuesday in config.time_slot_config.times.get("TUE", []):
            tue.append({"start": tuesday.start, "spacing": getattr(tuesday, "spacing", None), "end": tuesday.end})
        for wednesday in config.time_slot_config.times.get("WED", []):
            wed.append({"start": wednesday.start, "spacing": getattr(wednesday, "spacing", None), "end": wednesday.end})
        for thursday in config.time_slot_config.times.get("THU", []):
            thu.append({"start": thursday.start, "spacing": getattr(thursday, "spacing", None), "end": thursday.end})
        for friday in config.time_slot_config.times.get("FRI", []):
            fri.append({"start": friday.start, "spacing": getattr(friday, "spacing", None), "end": friday.end})

        # Extract classes info
        for clas in config.time_slot_config.classes:
            diction = {"credits": clas.credits, "meetings": get_met(clas)}
            if hasattr(clas, "disabled"):
                diction["disabled"] = clas.disabled
            classes.append(diction)

        #Extract faculty info with serialized times per day
        for member in config.config.faculty:
            faculty.append({
            "name": member.name,
            "maximum_credits": member.maximum_credits,
            "minimum_credits": member.minimum_credits,
            "unique_course_limit": member.unique_course_limit,
            "times": {
                "MON": serialize_time_ranges(member.times.get("MON", [])),
                "TUE": serialize_time_ranges(member.times.get("TUE", [])),
                "WED": serialize_time_ranges(member.times.get("WED", [])),
                "THU": serialize_time_ranges(member.times.get("THU", [])),
                "FRI": serialize_time_ranges(member.times.get("FRI", [])),
            }
        })

# Extract courses info
        for course in config.config.courses:
            courses.append({
        "course_id": course.course_id,
        "credits": course.credits,
        "room": course.room,
        "lab": course.lab,
        "conflicts": course.conflicts,
        "faculty": course.faculty
    })

# Final combined config dictionary
        final_config = {
    "config": {
        "rooms": config.config.rooms,
        "labs": config.config.labs,
        "courses": courses,
        "faculty": faculty
    },
    "time_slot_config": {
        "times": {
            "MON": mon,
            "TUE": tue,
            "WED": wed,
            "THU": thu,
            "FRI": fri,
        },
        "classes": classes
    },
    "limit": config.limit,
    "optimizer_flags": config.optimizer_flags
}
        with open(path, "w") as json_file:
            json.dump(final_config, json_file, indent=1)

def serialize_time_ranges(day_slots):
        result = []
        for slot in day_slots:
            item = {
                "start": slot.start,
                "end": slot.end,
            }
            # Only include spacing if the attribute exists
            if hasattr(slot, "spacing"):
                item["spacing"] = slot.spacing
            result.append(item)
        return result

def get_met(met):
        meetings = []
        for meet in met.meetings:
            diction = {"day": meet.day, "duration": meet.duration}
            if hasattr(meet, "lab"):
                diction["lab"] = meet.lab
            meetings.append(diction)
        return meetings



