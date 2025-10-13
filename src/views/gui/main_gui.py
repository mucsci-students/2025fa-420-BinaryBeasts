

import src.views.gui.roomGui as roomGui
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from src.views.gui.schedules_gui import SchedulesGUI
from PyQt5.QtWidgets import QInputDialog, QMessageBox
import src.views.gui.course_view_gui as course_view_gui
import json

from scheduler import (
    Scheduler,
    load_config_from_file,
)
from scheduler.config import CombinedConfig

num_schedules = 0

class MainGUI(QWidget):
    file_uploaded = False

    def __init__(self):
        config = any

        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('College Course Sceduler')
        self.setMinimumWidth(800)
        self.setMinimumHeight(800)
        layout = QVBoxLayout()

        title = QLabel('College Course Scheduler')
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)


        CourseButton = QPushButton('Edit Courses')
        CourseButton.setFont(QFont('Arial', 8))
        CourseButton.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;')
        layout.addWidget(CourseButton)
        CourseButton.clicked.connect(self.open_course_manager)

        FacultyButton = QPushButton('Edit Faculty')
        FacultyButton .setFont(QFont('Arial', 8))
        FacultyButton .setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;')
        layout.addWidget(FacultyButton)
        FacultyButton .clicked.connect(self.open_faculty_manager)


        LabButton = QPushButton('Edit Labs')
        LabButton.setFont(QFont('Arial', 8))
        LabButton.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;')
        layout.addWidget(LabButton)
        LabButton.clicked.connect(self.open_lab_manager)

        RoomButton = QPushButton('Edit Rooms')
        RoomButton.setFont(QFont('Arial', 8))
        RoomButton.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;')
        layout.addWidget(RoomButton)
        RoomButton.clicked.connect(self.open_room_manager)

        self.selected_label = QLabel('No file selected')
        self.selected_label.setFont(QFont('Arial', 10))
        self.selected_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.selected_label)

        SaveButton = QPushButton('Save Configuration File')
        SaveButton.setFont(QFont('Arial', 8))
        SaveButton.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;')
        layout.addWidget(SaveButton)
        SaveButton.clicked.connect(self.save_configuration)

        self.button = QPushButton('Upload Configuration File')
        self.button.setFont(QFont('Arial', 8))
        self.button.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;')
        layout.addWidget(self.button)
        self.button.clicked.connect(self.open_file_dialog)

        self.button = QPushButton('Upload Schedule')
        self.button.setFont(QFont('Arial', 8))
        self.button.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;')
        layout.addWidget(self.button)
        self.button.clicked.connect(self.load_schedule)

        GenerateButton = QPushButton('Generate Schedule')
        GenerateButton.setFont(QFont('Arial', 8))
        GenerateButton.setStyleSheet('padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;')
        layout.addWidget(GenerateButton)
        GenerateButton.clicked.connect(self.generate_schedule)


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
        #self.course_window = courses_gui.CoursesDialog(self.config)
        #
        #self.course_window.show()

    def open_lab_manager(self):
        if not self.file_uploaded:
            QMessageBox.critical(self, "Error", "Please upload a configuration file first.")
            return
        print("Lab Manager Opened")

    def open_faculty_manager(self):
        if not self.file_uploaded:
            QMessageBox.critical(self, "Error", "Please upload a configuration file first.")
            return
        print("Faculty Manager Opened")
    
    def open_room_manager(self):
        if not self.file_uploaded:
            QMessageBox.critical(self, "Error", "Please upload a configuration file first.")
            return
        #try:
        #    self.room_window = roomGui.RoomGUI(self.config)
         #   self.room_window.show()
        #except Exception as e:
         #   QMessageBox.critical(self, "Error", f"Failed to open Room Manager:\n{e}")
       

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
        print("Schedule Loaded")

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
# You can now json.dumps(final_config) safely without serialization errors


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



