import sys
from PyQt5.QtWidgets import ( # type : ignore
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QFileDialog,
    QLabel,
    QCheckBox,
    QDialogButtonBox,
    QDialog,
) # type : ignore
from PyQt5.QtGui import QFont # type : ignore
from PyQt5.QtCore import Qt # type : ignore
from src.views.gui.schedules_gui import SchedulesGUI
from PyQt5.QtWidgets import QInputDialog, QMessageBox # type : ignore
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


class MainGUI(QWidget):
    file_uploaded = False

    def __init__(self):

        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("College Course Scheduler")
        self.setMinimumWidth(800)
        self.setMinimumHeight(800)
        layout = QVBoxLayout()

        title = QLabel("College Course Scheduler")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        CourseButton = QPushButton("Edit Courses")
        CourseButton.setFont(QFont("Arial", 8))
        CourseButton.setStyleSheet(
            "padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;"
        )
        layout.addWidget(CourseButton)
        CourseButton.clicked.connect(self.open_course_manager)

        FacultyButton = QPushButton("Edit Faculty")
        FacultyButton.setFont(QFont("Arial", 8))
        FacultyButton.setStyleSheet(
            "padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;"
        )
        layout.addWidget(FacultyButton)
        FacultyButton.clicked.connect(self.open_faculty_manager)

        LabButton = QPushButton("Edit Labs")
        LabButton.setFont(QFont("Arial", 8))
        LabButton.setStyleSheet(
            "padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;"
        )
        layout.addWidget(LabButton)
        LabButton.clicked.connect(self.open_lab_manager)

        RoomButton = QPushButton("Edit Rooms")
        RoomButton.setFont(QFont("Arial", 8))
        RoomButton.setStyleSheet(
            "padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;"
        )
        layout.addWidget(RoomButton)
        RoomButton.clicked.connect(self.open_room_manager)

        self.selected_label = QLabel("No file selected")
        self.selected_label.setFont(QFont("Arial", 10))
        self.selected_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.selected_label)

        SaveButton = QPushButton("Save Configuration File")
        SaveButton.setFont(QFont("Arial", 8))
        SaveButton.setStyleSheet(
            "padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;"
        )
        layout.addWidget(SaveButton)
        SaveButton.clicked.connect(self.save_configuration)

        self.button = QPushButton("Upload Configuration File")
        self.button.setFont(QFont("Arial", 8))
        self.button.setStyleSheet(
            "padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;"
        )
        layout.addWidget(self.button)
        self.button.clicked.connect(self.open_file_dialog)

        self.button = QPushButton("Upload Schedule")
        self.button.setFont(QFont("Arial", 8))
        self.button.setStyleSheet(
            "padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;"
        )
        layout.addWidget(self.button)
        self.button.clicked.connect(self.load_schedule)

        GenerateButton = QPushButton("Generate Schedule")
        GenerateButton.setFont(QFont("Arial", 8))
        GenerateButton.setStyleSheet(
            "padding: 10px; background-color: #4CAF50; color: white; border-radius: 5px; width: 100px;"
        )
        layout.addWidget(GenerateButton)
        GenerateButton.clicked.connect(self.generate_schedule)

        self.setLayout(layout)

    def open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open JSON file", "", "JSON Files (*.json)"
        )
        if file_path:
            self.file_uploaded = True
            config_obj = load_config_from_file(CombinedConfig, file_path)
            self.config = config_obj
            self.selected_label.setText(f"Selected: {file_path}")
            return
        else:
            self.selected_label.setText("No file selected.")

    def open_course_manager(self):
        if not self.file_uploaded:
            QMessageBox.critical(
                self, "Error", "Please upload a configuration file first."
            )
            return

        try:
            course_manager = CourseManager()
            courses_data = []
            for course in self.config.config.courses:
                courses_data.append(
                    {
                        "course_id": course.course_id,
                        "credits": course.credits,
                        "room": list(course.room)
                        if hasattr(course.room, "__iter__")
                        else [course.room],
                        "lab": list(course.lab)
                        if hasattr(course.lab, "__iter__")
                        else [course.lab],
                        "faculty": list(course.faculty)
                        if hasattr(course.faculty, "__iter__")
                        else [course.faculty],
                        "conflicts": list(course.conflicts)
                        if hasattr(course.conflicts, "__iter__")
                        else [course.conflicts],
                    }
                )

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
            QMessageBox.critical(
                self, "Error", "Please upload a configuration file first."
            )
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
            QMessageBox.critical(
                self, "Error", "Please upload a configuration file first."
            )
            return
        try:
            # Create FacultyManager and load faculty from config
            faculty_manager = FacultyManager()
            faculty_data = []
            for faculty in self.config.config.faculty:
                faculty_data.append(
                    {
                        "name": faculty.name,
                        "minimum_credits": faculty.minimum_credits,
                        "maximum_credits": faculty.maximum_credits,
                        "unique_course_limit": faculty.unique_course_limit,
                        "times": dict(faculty.times)
                        if hasattr(faculty, "times")
                        else {},
                        "course_preferences": dict(faculty.course_preferences)
                        if hasattr(faculty, "course_preferences")
                        else {},
                        "room_preferences": dict(faculty.room_preferences)
                        if hasattr(faculty, "room_preferences")
                        else {},
                        "lab_preferences": dict(faculty.lab_preferences)
                        if hasattr(faculty, "lab_preferences")
                        else {},
                    }
                )

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
            QMessageBox.critical(
                self, "Error", "Please upload a configuration file first."
            )
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
            QMessageBox.critical(
                self, "Error", "Please upload a configuration file first."
            )
            return
        folder_path = QFileDialog.getSaveFileName(
            self, "Select Directory", "config.json", "JSON Files (*.json)"
        )[0]

        if folder_path:
            try:
                save_config(self.config, folder_path)
                QMessageBox.information(
                    self, "Success", f"Configuration saved to {folder_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to save configuration:\n{e}"
                )
        else:
            self.selected_label.setText("No folder selected.")

    def generate_schedule(self):
        if not self.file_uploaded:
            QMessageBox.critical(
                self, "Error", "Please upload a configuration file first."
            )
            return
        num, ok = QInputDialog.getInt(
            self, "Input Required", "Pick an amount of schedules to generate:", min=1
        )
        if not ok:
            return
        opt_dialog = QDialog(self)
        opt_dialog.setWindowTitle("Optimization Options")
        opt_layout = QVBoxLayout(opt_dialog)
        opt_layout.addWidget(QLabel("Select optimization options:"))

        cb_fac_course = QCheckBox("Optimize faculty course")
        cb_fac_room = QCheckBox("Optimize faculty room")
        cb_fac_lab = QCheckBox("Optimize faculty lab")
        cb_same_room = QCheckBox("Same room")
        cb_same_lab = QCheckBox("Same lab")
        cb_pack_rooms = QCheckBox("Pack rooms")
        cb_pack_labs = QCheckBox("Pack labs")

        # Map checkboxes to flag names
        flag_map = [
            (cb_fac_course, "faculty_course"),
            (cb_fac_room, "faculty_room"),
            (cb_fac_lab, "faculty_lab"),
            (cb_same_room, "same_room"),
            (cb_same_lab, "same_lab"),
            (cb_pack_rooms, "pack_rooms"),
            (cb_pack_labs, "pack_labs"),
        ]
        # Pre-fill from existing config flags if available
        existing_flags = getattr(self.config, "optimizer_flags", None)
        if isinstance(existing_flags, (list, set, tuple)):
            for cb, name in flag_map:
                cb.setChecked(name in existing_flags)
        elif isinstance(existing_flags, dict):
            for cb, name in flag_map:
                cb.setChecked(existing_flags.get(name, False))

        for cb, _ in flag_map:
            opt_layout.addWidget(cb)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(opt_dialog.accept)
        buttons.rejected.connect(opt_dialog.reject)
        opt_layout.addWidget(buttons)

        if opt_dialog.exec_() == QDialog.Accepted:
            # store as a list of strings for enabled options
            selected_flags = [name for cb, name in flag_map if cb.isChecked()]
            self.config.optimizer_flags = selected_flags
        try:
            # Generate schedules using the Scheduler
            scheduler = Scheduler(self.config)
            schedules = []
            for i, schedule in enumerate(scheduler.get_models()):
                schedules.append(schedule)
                if i + 1 >= num:
                    break

            if not schedules:
                QMessageBox.warning(
                    self, "No Schedules", "No valid schedules could be generated."
                )
                return

            # Close current window and open schedule viewer with the generated schedules
            self.close()
            self.generate_schedule_window = SchedulesGUI(
                schedules=schedules, config=self.config
            )
            self.generate_schedule_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate schedules:\n{e}")

    def load_schedule(self):
        if not self.file_uploaded:
            QMessageBox.critical(
                self, "Error", "Please upload a configuration file first."
            )
            return
        """Load a previously saved schedule from JSON or CSV file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Schedule File",
            "",
            "Schedule Files (*.json *.csv);;JSON Files (*.json);;CSV Files (*.csv)",
        )

        if not file_path:
            return

        try:
            # Parse the schedule file
            if file_path.endswith(".json"):
                schedules = self._load_schedule_from_json(file_path)
            elif file_path.endswith(".csv"):
                schedules = self._load_schedule_from_csv(file_path)
            else:
                QMessageBox.critical(
                    self, "Error", "Unsupported file format. Please use JSON or CSV."
                )
                return

            if not schedules:
                QMessageBox.warning(
                    self, "No Schedules", "No schedules found in the file."
                )
                return

            # Close current window and open schedule viewer
            self.close()
            self.generate_schedule_window = SchedulesGUI(
                schedules=schedules, config=self.config
            )
            self.generate_schedule_window.show()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load schedule:\n{e}")

    def _load_schedule_from_json(self, file_path):
        """Load schedules from JSON file."""
        with open(file_path, "r") as f:
            data = json.load(f)

        schedules = []

        # Handle two possible JSON formats:
        # 1. Array of objects with schedule_id and courses fields
        # 2. Simple array of arrays of course CSV strings
        for schedule_data in data:
            schedule = []

            # Format 1: Object with 'courses' field
            if isinstance(schedule_data, dict) and "courses" in schedule_data:
                for course_csv in schedule_data["courses"]:
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

        with open(file_path, "r") as f:
            reader = csv.reader(f)
            for row in reader:
                # Empty row separates schedules
                if not row or all(cell.strip() == "" for cell in row):
                    if current_schedule:
                        schedules.append(current_schedule)
                        current_schedule = []
                    continue

                # Skip header rows
                if row[0].startswith("Schedule") or row[0].startswith("Course"):
                    continue

                # Reconstruct CSV format from row
                course_csv = ",".join(row)
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
        Scheduler(self.config)


if __name__ == "__main__":
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
        mon.append(
            {
                "start": monday.start,
                "spacing": getattr(monday, "spacing", None),
                "end": monday.end,
            }
        )
    for tuesday in config.time_slot_config.times.get("TUE", []):
        tue.append(
            {
                "start": tuesday.start,
                "spacing": getattr(tuesday, "spacing", None),
                "end": tuesday.end,
            }
        )
    for wednesday in config.time_slot_config.times.get("WED", []):
        wed.append(
            {
                "start": wednesday.start,
                "spacing": getattr(wednesday, "spacing", None),
                "end": wednesday.end,
            }
        )
    for thursday in config.time_slot_config.times.get("THU", []):
        thu.append(
            {
                "start": thursday.start,
                "spacing": getattr(thursday, "spacing", None),
                "end": thursday.end,
            }
        )
    for friday in config.time_slot_config.times.get("FRI", []):
        fri.append(
            {
                "start": friday.start,
                "spacing": getattr(friday, "spacing", None),
                "end": friday.end,
            }
        )

    # Extract classes info
    for clas in config.time_slot_config.classes:
        diction = {"credits": clas.credits, "meetings": get_met(clas)}
        if hasattr(clas, "disabled"):
            diction["disabled"] = clas.disabled
        classes.append(diction)

    # Extract faculty info with serialized times per day
    for member in config.config.faculty:
        faculty.append(
            {
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
                },
            }
        )

    # Extract courses info
    for course in config.config.courses:
        courses.append(
            {
                "course_id": course.course_id,
                "credits": course.credits,
                "room": course.room,
                "lab": course.lab,
                "conflicts": course.conflicts,
                "faculty": course.faculty,
            }
        )

    # Final combined config dictionary
    final_config = {
        "config": {
            "rooms": config.config.rooms,
            "labs": config.config.labs,
            "courses": courses,
            "faculty": faculty,
        },
        "time_slot_config": {
            "times": {
                "MON": mon,
                "TUE": tue,
                "WED": wed,
                "THU": thu,
                "FRI": fri,
            },
            "classes": classes,
        },
        "limit": config.limit,
        "optimizer_flags": config.optimizer_flags,
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
