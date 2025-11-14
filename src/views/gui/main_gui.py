import sys
from PyQt5.QtWidgets import (
    QWidget, QFileDialog, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QInputDialog, QMessageBox,
    QDialog, QCheckBox, QDialogButtonBox, QProgressDialog, QApplication
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from src.views.gui.schedules_gui import SchedulesGUI
from src.views.gui.ai_chat_gui import AIChatDialog
from src.conflict_resolution import ConflictResolutionObserver
from src.controllers.course_controller import CourseController
from src.controllers.room_controller import RoomController
from src.controllers.faculty_controller import FacultyController
from src.controllers.lab_controller import LabController
from src.controllers.nl_controller import NLController
from src.models.course_model import CourseManager
from src.models.room_model import RoomManager
from src.models.faculty_model import FacultyManager
from src.models.lab_model import LabManager
# Controllers and models are now handled by the factory pattern
from src.views.gui.dialog_factory import DialogFactory, DialogType
# Controllers and models are now handled by the factory pattern
import json
from scheduler import (
    Scheduler,
    load_config_from_file,
)
from scheduler.config import CombinedConfig

num_schedules = 0
LABEL_FONT = QFont('Arial', 16, QFont.Bold)
FONT = QFont("Arial", 13)

FRAME_STYLE = """
QFrame {
  background-color: palette(Base);
  border: 1px solid palette(Midlight);
  border-radius: 10px;
  padding: 12px;
}
"""

BUTTON_STYLE = """
QPushButton {
  padding: 6px 12px;
  background-color: #327f66;   /* your green */
  color: white;
  border-radius: 8px;
  border: none;
  font-weight: 600;
}
QPushButton:hover {
  background-color: #3da879;   /* lighter green on hover */
}
QPushButton:pressed {
  background-color: #2a6a52;   /* darker green when pressed */
}
QPushButton:disabled {
  background-color: palette(Mid);
  color: palette(Midlight);
}
"""

class ScheduleGeneratorWorker(QObject):
    """Worker class to generate schedules in a separate thread."""
    progress = pyqtSignal(int)  # Signal to emit current progress
    finished = pyqtSignal(list)  # Signal to emit completed schedules
    error = pyqtSignal(str)  # Signal to emit errors

    def __init__(self, config, num_schedules):
        super().__init__()
        self.config = config
        self.num_schedules = num_schedules
        self._is_cancelled = False

    def run(self):
        """Generate schedules and emit progress updates."""
        try:
            scheduler = Scheduler(self.config)
            schedules = []

            for i, schedule in enumerate(scheduler.get_models()):
                if self._is_cancelled:
                    break

                schedules.append(schedule)
                self.progress.emit(i + 1)  # Emit progress

                if i + 1 >= self.num_schedules:
                    break

            if schedules and not self._is_cancelled:
                self.finished.emit(schedules)
            elif not self._is_cancelled:
                self.error.emit("No valid schedules could be generated.")

        except Exception as e:
            self.error.emit(str(e))

    def cancel(self):
        """Cancel the schedule generation."""
        self._is_cancelled = True

class MainGUI(QWidget):
    file_uploaded = False

    def __init__(self):

        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Scheduler")
        self.setMinimumWidth(860)
        self.setMinimumHeight(580)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        # Header
        title = QLabel("College Course Scheduler")
        title.setFont(LABEL_FONT)
        title.setAlignment(Qt.AlignCenter)  # type: ignore[attr-defined]
        layout.addWidget(title)

        # config section
        config_section = QFrame()
        config_section.setStyleSheet(FRAME_STYLE)
        cfg = QVBoxLayout(config_section)
        cfg.setContentsMargins(10, 6, 10, 6)
        cfg.setSpacing(10)

        self.selected_label = QLabel("No file selected")
        self.selected_label.setFont(FONT)
        self.selected_label.setStyleSheet("color:#cccccc;")
        self.selected_label.setAlignment(Qt.AlignCenter)  # type: ignore[attr-defined]
        cfg.addWidget(self.selected_label)

        config_buttons = QHBoxLayout()
        config_buttons.setSpacing(8)

        upload_config_btn = QPushButton("Upload Configuration File")
        upload_config_btn.setStyleSheet(BUTTON_STYLE)
        upload_config_btn.setMinimumHeight(32)
        upload_config_btn.clicked.connect(self.open_file_dialog)

        upload_schedule_btn = QPushButton("Upload Schedule")
        upload_schedule_btn.setStyleSheet(BUTTON_STYLE)
        upload_schedule_btn.setMinimumHeight(32)
        upload_schedule_btn.clicked.connect(self.load_schedule)

        save_btn = QPushButton("Save Configuration File")
        save_btn.setStyleSheet(BUTTON_STYLE)
        save_btn.setMinimumHeight(32)
        save_btn.clicked.connect(self.save_configuration)

        ai_chat_btn = QPushButton("💬 AI Assistant")
        ai_chat_btn.setStyleSheet(BUTTON_STYLE)
        ai_chat_btn.setMinimumHeight(32)
        ai_chat_btn.clicked.connect(self.open_ai_chat)

        config_buttons.addWidget(upload_config_btn)
        config_buttons.addWidget(upload_schedule_btn)
        config_buttons.addStretch(1)
        config_buttons.addWidget(ai_chat_btn)
        config_buttons.addWidget(save_btn)

        cfg.addLayout(config_buttons)
        layout.addWidget(config_section)

        # edit section
        edit_section = QFrame()
        edit_section.setStyleSheet(FRAME_STYLE)
        edit_layout = QVBoxLayout(edit_section)
        edit_layout.setContentsMargins(8, 8, 8, 8)

        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)

        def make_edit_btn(label, slot):
            btn = QPushButton(label)
            btn.setStyleSheet(BUTTON_STYLE)
            btn.setMinimumHeight(32)
            btn.setMinimumWidth(100)
            btn.clicked.connect(slot)
            return btn

        courses_btn = make_edit_btn("Edit Courses", self.open_course_manager)
        faculty_btn = make_edit_btn("Edit Faculty", self.open_faculty_manager)
        labs_btn = make_edit_btn("Edit Labs", self.open_lab_manager)
        rooms_btn = make_edit_btn("Edit Rooms", self.open_room_manager)
        timeslots_btn = make_edit_btn("Edit Time Slots", self.open_timeslot_manager)

        grid.addWidget(courses_btn, 0, 0)
        grid.addWidget(faculty_btn, 0, 1)
        grid.addWidget(labs_btn, 1, 0)
        grid.addWidget(rooms_btn, 1, 1)
        grid.addWidget(timeslots_btn, 2, 0)

        edit_layout.addLayout(grid)
        layout.addWidget(edit_section)

        # generate section
        generate_section = QFrame()
        generate_section.setStyleSheet(FRAME_STYLE)
        gen = QVBoxLayout(generate_section)
        gen.setContentsMargins(10, 6, 10, 6)
        gen.setSpacing(10)

        generate_btn = QPushButton("Generate Schedule")
        generate_btn.setStyleSheet(BUTTON_STYLE)
        generate_btn.setMinimumHeight(36)
        generate_btn.clicked.connect(self.generate_schedule)
        generate_btn.setCursor(Qt.PointingHandCursor)  # type: ignore[attr-defined]
        gen.addWidget(generate_btn, alignment=Qt.AlignCenter)  # type: ignore[attr-defined]

        layout.addWidget(generate_section)
        layout.addStretch(1)

        # Initialize conflict resolution observer
        self._setup_conflict_observer()

        self.setLayout(layout)

    def open_file_dialog(self):
            file_path, _ = QFileDialog.getOpenFileName(self, 'Open JSON file', '', 'JSON Files (*.json)')
            if file_path:
                self.file_uploaded = True
                config_obj = load_config_from_file(CombinedConfig, file_path)
                self.config = config_obj
                
                # Register the CombinedConfig with conflict observer for automatic updates
                if hasattr(self, 'conflict_observer'):
                    self.conflict_observer.register_combined_config(self.config)
                
                file_name = file_path.split('/')[-1]
                self.selected_label.setText(f"<span style='font-size: 13px; color: green;'>'"
                                            f"{file_name}' successfully uploaded</span>")
                return
            else:
                self.selected_label.setText('No file selected.')

    def _setup_conflict_observer(self):
        """
        Setup conflict resolution observer for cross-manager dependency handling.
        
        This observer handles conflicts when entities are deleted or renamed,
        automatically updating references in related managers.
        """
        # Create conflict resolution observer for cross-manager dependency handling
        self.conflict_observer = ConflictResolutionObserver()

    def _attach_conflict_observer_to_manager(self, manager, manager_type: str):
        """
        Attach conflict resolution observer to a manager for cross-manager dependency handling.
        
        Args:
            manager: An Observable manager (CourseManager, FacultyManager, etc.)
            manager_type: Type of manager for conflict resolution ('course', 'faculty', 'lab', 'room')
        """
        # Attach conflict resolution observer only
        if hasattr(manager, 'add_observer') and hasattr(self, 'conflict_observer'):
            manager.add_observer(self.conflict_observer)
            
        # Register manager with conflict resolver for cross-manager dependency handling
        if manager_type and hasattr(self, 'conflict_observer'):
            self.conflict_observer.register_manager(manager_type, manager)

    def open_course_manager(self):
        """Open the course management dialog using the factory pattern."""
        if not self.file_uploaded:
            QMessageBox.critical(
                self, "Error", "Please upload a configuration file first."
            )
            return

        try:
            # Use factory to create the courses dialog with observer support
            self.course_window = DialogFactory.create_dialog(
                DialogType.COURSES, 
                self.config, 
                self,
                self.conflict_observer
            )
            self.course_window.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Course Manager:\n{e}")

    def open_lab_manager(self):
        """Open the lab management dialog using the factory pattern."""
        if not self.file_uploaded:
            QMessageBox.critical(
                self, "Error", "Please upload a configuration file first."
            )
            return

        try:
            # Use factory to create the labs dialog with observer support
            self.lab_window = DialogFactory.create_dialog(
                DialogType.LABS, 
                self.config, 
                self,
                self.conflict_observer
            )
            self.lab_window.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Lab Manager:\n{e}")

    def open_faculty_manager(self):
        """Open the faculty management dialog using the factory pattern."""
        if not self.file_uploaded:
            QMessageBox.critical(
                self, "Error", "Please upload a configuration file first."
            )
            return

        try:
            # Use factory to create the faculty dialog with observer support
            self.faculty_window = DialogFactory.create_dialog(
                DialogType.FACULTY, 
                self.config, 
                self,
                self.conflict_observer
            )
            self.faculty_window.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Faculty Manager:\n{e}")

        print("Faculty Manager Opened")

    def open_room_manager(self):
        """Open the room management dialog using the factory pattern."""
        if not self.file_uploaded:
            QMessageBox.critical(
                self, "Error", "Please upload a configuration file first."
            )
            return

        try:
            # Use factory to create the rooms dialog with observer support
            self.room_window = DialogFactory.create_dialog(
                DialogType.ROOMS, 
                self.config, 
                self,
                self.conflict_observer
            )
            self.room_window.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Room Manager:\n{e}")

    def open_timeslot_manager(self):
        """Open the time slot management dialog using the factory pattern."""
        if not self.file_uploaded:
            QMessageBox.critical(
                self, "Error", "Please upload a configuration file first."
            )
            return

        try:
            # Use factory to create the time slots dialog with observer support
            self.timeslot_window = DialogFactory.create_dialog(
                DialogType.TIMESLOTS, 
                self.config, 
                self,
                self.conflict_observer
            )
            self.timeslot_window.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Time Slot Manager:\n{e}")

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

    def open_ai_chat(self):
        """Open AI Assistant chat dialog."""
        if not self.file_uploaded:
            QMessageBox.critical(
                self, "Error", "Please upload a configuration file first."
            )
            return

        try:
            # Create managers and controllers
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
            course_controller = CourseController(course_manager)

            # Create faculty controller
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
            faculty_controller = FacultyController(faculty_manager)

            # Create lab and room controllers
            lab_manager = LabManager(self.config)
            lab_controller = LabController(lab_manager)

            room_manager = RoomManager(self.config)
            room_controller = RoomController(room_manager)

            # Create NL controller with all controllers and config
            nl_controller = NLController(
                config=self.config,
                course_controller=course_controller,
                faculty_controller=faculty_controller,
                lab_controller=lab_controller,
                room_controller=room_controller
            )

            # Open chat dialog
            self.chat_window = AIChatDialog(nl_controller, self)
            self.chat_window.exec_()

            # Check if schedules were generated
            if hasattr(self.chat_window, 'generated_schedules') and self.chat_window.generated_schedules:
                schedules = self.chat_window.generated_schedules
                # Close main window and open schedule viewer
                self.close()
                self.generate_schedule_window = SchedulesGUI(schedules=schedules, config=self.config)
                self.generate_schedule_window.show()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open AI Assistant:\n{e}")

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
        else:
            # User cancelled optimization dialog
            return

        # Create progress dialog
        progress = QProgressDialog(
            "Generating schedules...",
            None,  # No cancel button
            0,
            num,
            self
        )
        progress.setWindowTitle("Generating Schedules")
        progress.setWindowModality(Qt.WindowModal)  # type: ignore[attr-defined]
        progress.setMinimumDuration(0)  # Show immediately
        progress.setValue(0)
        progress.setCancelButton(None)  # Remove cancel button

        # Create worker thread
        self.thread = QThread()
        self.worker = ScheduleGeneratorWorker(self.config, num)
        self.worker.moveToThread(self.thread)

        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(progress.setValue)
        self.worker.finished.connect(lambda schedules: self._on_schedules_generated(schedules, progress))
        self.worker.error.connect(lambda error: self._on_generation_error(error, progress))
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)

        # Start the thread
        self.thread.start()

    def _on_schedules_generated(self, schedules, progress):
        """Handle successful schedule generation."""
        progress.close()

        if not schedules:
            QMessageBox.warning(self, "No Schedules", "No valid schedules could be generated.")
            return

        # hide current window and open schedule viewer
        self.hide()
        self.generate_schedule_window = SchedulesGUI(schedules=schedules, config=self.config, parent_gui=self)
        self.generate_schedule_window.show()

    def _on_generation_error(self, error_message, progress):
        """Handle schedule generation errors."""
        progress.close()
        QMessageBox.critical(self, "Error", f"Failed to generate schedules:\n{error_message}")

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
            self.hide()
            self.generate_schedule_window = SchedulesGUI(
                schedules=schedules, config=self.config, parent_gui=self
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