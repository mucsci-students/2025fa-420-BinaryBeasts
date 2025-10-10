import os
import sys
# Ensure Python can resolve the top-level 'src' package when running this file directly
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import src.views.gui.roomGui as roomGui
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import src.views.gui.generate_schedules_gui as generate_schedules_gui
from PyQt5.QtWidgets import QInputDialog, QMessageBox
import src.views.gui.courses_gui as courses_gui



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
        # Remember the path of the loaded config file (if any) so editors can overwrite it.
        self.config_path = None
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
    
    # --- helpers ---
    def _dump_config_dict(self, cfg):
        """Return a plain dict for the scheduler config, regardless of Pydantic model/dict input."""
        try:
            if hasattr(cfg, "model_dump"):
                return cfg.model_dump()
        except Exception:
            pass
        return cfg

    def _save_config(self, cfg, path: str):
        data = self._dump_config_dict(cfg)
        # If the dict is the raw scheduler shape, allow both raw or wrapped; prefer raw for user files
        if isinstance(data, dict) and "config" in data:
            serializable = data
        else:
            serializable = {"config": data} if isinstance(data, dict) else data
        import json as _json
        with open(path, "w", encoding="utf-8") as f:
            _json.dump(serializable, f, indent=2, ensure_ascii=False)

    def _generate_schedules(self, cfg, num: int):
        # Use the scheduler directly; cfg can be a Pydantic CombinedConfig or compatible dict
        try:
            scheduler = Scheduler(cfg)
        except Exception:
            # If cfg is a dict, try to validate to CombinedConfig first
            try:
                validated = CombinedConfig.model_validate(self._dump_config_dict(cfg))
                scheduler = Scheduler(validated)
            except Exception as e:
                raise e
        # This placeholder iterates models to ensure generation runs
        for _ in scheduler.get_models(limit=num if hasattr(scheduler, 'get_models') else None):
            break
    def open_file_dialog(self):
            file_path, _ = QFileDialog.getOpenFileName(self, 'Open JSON file', '', 'JSON Files (*.json)')
            if file_path:
                self.file_uploaded = True
                config_obj = load_config_from_file(CombinedConfig, file_path)
                self.config = config_obj
                # Remember the path so child dialogs (e.g., RoomGUI) can save back to the same file
                self.config_path = file_path
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
        try:
            cfg = self.config
            # Normalize pydantic model to dict if needed; RoomGUI can also handle this,
            # but we keep it explicit here for clarity and resilience.
            if hasattr(cfg, "model_dump"):
                cfg = cfg.model_dump()
            # If top-level looks like scheduler raw config, wrap under 'config' key for RoomManager
            if isinstance(cfg, dict) and "config" not in cfg:
                if any(k in cfg for k in ("rooms", "courses", "faculty", "labs")):
                    cfg = {"config": cfg}

            self.room_window = roomGui.RoomGUI(cfg, loaded_path=self.config_path)
            self.room_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Room Manager:\n{e}")
       

    def save_configuration(self):
        if not self.file_uploaded:
            QMessageBox.critical(self, "Error", "Please upload a configuration file first.")
            return
        folder_path = QFileDialog.getSaveFileName(self, "Select Directory", "config.json", "JSON Files (*.json)")[0]

        if folder_path:  
            self._save_config(self.config, folder_path)
        else:
            self.selected_label.setText('No folder selected.')

    def generate_schedule(self): 
        if not self.file_uploaded:
            QMessageBox.critical(self, "Error", "Please upload a configuration file first.")
            return       
        num, ok = QInputDialog.getInt(self, "Input Required", "Pick an amount of schedules to generate:", min=1)
        if not ok:
            return
        self.close()
        # Run generation (basic check) and open result GUI
        self._generate_schedules(self.config, num)
        self.generate_schedule_window = generate_schedules_gui.MainGUI()
        self.generate_schedule_window.show()
    
    def load_schedule(self):
        print("Schedule Loaded")

    def gen_sched(self):
        scheduler = Scheduler(self.config)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MainGUI()
    gui.show()
    sys.exit(app.exec_())