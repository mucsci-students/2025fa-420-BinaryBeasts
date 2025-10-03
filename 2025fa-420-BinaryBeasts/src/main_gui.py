

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
try:
    from roomGUI import create_room_window  # Factory handles construction & fallback
except Exception:  # pragma: no cover - defensive import fallback
    create_room_window = None  # type: ignore




class MainGUI(QWidget):
    def __init__(self):
        super().__init__()
        # State: path to currently selected configuration file (lazy-loaded for Room GUI)
        self.loaded_config_path = None  # type: ignore[assignment]
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
        file_path, _ = QFileDialog.getOpenFileName(self,'Open JSON file','','JSON Files (*.json)')
        if file_path:
            self.loaded_config_path = file_path
            self.selected_label.setText(f"Selected: {file_path}")
            print(f"Selected config file path: {file_path}")
        else:
            self.selected_label.setText('No file selected.')

        
    def open_course_manager(self):
        print("Course Manager Opened")

    def open_lab_manager(self):
        print("Lab Manager Opened")

    def open_faculty_manager(self):
        print("Faculty Manager Opened")
    
    def open_room_manager(self):
        cfg = None
        loaded_path = self.loaded_config_path

        # If a path was previously selected, attempt to load lazily
        if loaded_path:
            try:
                import json
                with open(loaded_path, encoding='utf-8') as f:
                    cfg = json.load(f)
            except Exception as e:
                print(f"Failed to load stored config {loaded_path}: {e}")
                cfg = None

        # If still no config, prompt once now.
        if cfg is None:
            file_path, _ = QFileDialog.getOpenFileName(self, 'Select Room Config', '', 'JSON Files (*.json)')
            if file_path:
                try:
                    import json
                    with open(file_path, encoding='utf-8') as f:
                        cfg = json.load(f)
                    loaded_path = file_path
                    self.loaded_config_path = file_path  # remember for future
                    self.selected_label.setText(f"Selected: {file_path}")
                except Exception as e:
                    print(f"Failed to load {file_path}: {e}")
                    cfg = None

        # Create RoomGUI (top-level). If cfg is None the factory warns.
        self.room_window = create_room_window(cfg, loaded_path=loaded_path, parent=None)
        if self.room_window is not None:
            # Optional: ensure it stays on top when first opened
            try:
                self.room_window.setWindowFlags(self.room_window.windowFlags())
            except Exception:
                pass
            self.room_window.show()
            self.room_window.raise_()
            self.room_window.activateWindow()

    def save_configuration(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Directory", "")

        if folder_path:  
            self.selected_label.setText(f'Selected Folder: {folder_path}')
        else:
            self.selected_label.setText('No folder selected.')

    def generate_schedule(self):
        print("Schedule Generated")
    
    def load_schedule(self):
        print("Schedule Loaded")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = MainGUI()
    gui.show()
    sys.exit(app.exec_())