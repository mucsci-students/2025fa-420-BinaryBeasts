from __future__ import annotations

from typing import List
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QComboBox
)
from PyQt5.QtGui import QFont, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QRect

from src.controllers.schedules_controller import generate_controller
from src.models.room_day_model import schedule_to_location_blocks, min_max_hours, TimeBlock


DAY_LABELS = ["MON", "TUE", "WED", "THU", "FRI"]
DAY_WIDTH = 110
DAY_PADDING = 2
LEFT_MARGIN = 45
TEXT_OFFSET = 50
CANVAS_PADDING = 2


def _key_color(key: str) -> QColor:
    # Deterministic color hashed from an arbitrary key (course id)
    h = 0x10293847
    for ch in key:
        h = (h ^ ord(ch)) * 2654435761 & 0xFFFFFFFF
    hue = h % 360
    # Convert to RGB approx via HSV
    color = QColor()
    color.setHsv(hue, 200, 180)
    return color


class RoomPanel(QWidget):
    """Canvas panel that draws one location (room or lab) schedule across days."""
    def __init__(self, title: str, blocks: List[TimeBlock], parent=None):
        super().__init__(parent)
        self.title = title
        self.blocks = blocks
        self.min_h, self.max_h = min_max_hours(blocks)
        self.setMinimumWidth(LEFT_MARGIN + 5 * DAY_WIDTH + 10)
        # Height based on minute span
        height = (self.max_h - self.min_h) * 60 + 2 * CANVAS_PADDING + 50
        self.setMinimumHeight(max(120, height))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Title
        p.setFont(QFont("Arial", 12, QFont.Bold))
        p.drawText(10, 18, self.title)

        # Day labels
        p.setFont(QFont("Arial", 9))
        x0 = LEFT_MARGIN
        for i, label in enumerate(DAY_LABELS):
            x = x0 + i * DAY_WIDTH
            p.drawText(x + 10, 36, label)

        # Time grid lines and labels
        y0 = 50
        pen_grid = QPen(QColor(200, 200, 200))
        p.setPen(pen_grid)
        for hour in range(self.min_h, self.max_h + 1):
            y = y0 + (hour - self.min_h) * 60
            p.drawLine(0, y, LEFT_MARGIN + 5 * DAY_WIDTH, y)
            # time text on left
            p.setPen(QPen(Qt.black))
            ap = "PM" if hour >= 12 else "AM"
            hh = hour - 12 if hour > 12 else hour
            p.drawText(5, y + 12, f"{hh}:00{ap}")
            p.setPen(pen_grid)

        # Draw blocks
        for b in self.blocks:
            x = LEFT_MARGIN + (b.day - 1) * DAY_WIDTH + DAY_PADDING
            y = y0 + (b.start - self.min_h * 60) + CANVAS_PADDING
            w = DAY_WIDTH - 2 * DAY_PADDING
            h = max(6, b.duration)

            rect = QRect(x, y, w, h)
            # Color by course id (consistent across schedules)
            color = _key_color(b.course)
            # Slightly different tone for lab blocks
            fill = QColor(color)
            if getattr(b, "is_lab", False):
                fill = QColor(min(color.red() + 30, 255), min(color.green() + 30, 255), min(color.blue() + 30, 255))
            p.fillRect(rect, fill)

            # Prepare fonts and metrics
            title_font = QFont("Arial", 9, QFont.Bold)
            info_font = QFont("Arial", 8)
            fm_title = p.fontMetrics()
            p.setFont(title_font)
            fm_title = p.fontMetrics()
            p.setFont(info_font)
            fm_info = p.fontMetrics()

            # Determine how many lines fit
            padding = 2
            needed_two = padding + fm_title.height() + 2 + fm_info.height() + padding
            needed_one = padding + fm_title.height() + padding

            # Build strings
            title_text = b.course + (" (Lab)" if getattr(b, "is_lab", False) else "")
            extra = b.faculty
            if getattr(b, "is_lab", False) and getattr(b, "lab_name", None):
                extra += f" @ {b.lab_name}"

            # Clip drawing to the block rect and elide long text
            p.save()
            p.setClipRect(rect)
            p.setPen(QPen(Qt.black))

            if h >= needed_two:
                # Two lines
                p.setFont(title_font)
                fm = p.fontMetrics()
                title_elided = fm.elidedText(title_text, Qt.ElideRight, max(0, w - 8))
                baseline1 = y + padding + fm.ascent()
                p.drawText(x + 4, baseline1, title_elided)

                p.setFont(info_font)
                fm2 = p.fontMetrics()
                extra_elided = fm2.elidedText(extra, Qt.ElideRight, max(0, w - 8))
                baseline2 = baseline1 + 2 + fm2.ascent() + (fm.title.height() - fm.ascent() if False else 0)
                # Simpler: next line at title height + small gap
                baseline2 = y + padding + fm.height() + 2 + fm2.ascent()
                p.drawText(x + 4, baseline2, extra_elided)
            elif h >= needed_one:
                # One line: title only
                p.setFont(title_font)
                fm = p.fontMetrics()
                title_elided = fm.elidedText(title_text, Qt.ElideRight, max(0, w - 8))
                baseline1 = y + padding + fm.ascent()
                p.drawText(x + 4, baseline1, title_elided)
            else:
                # Not enough space for text; leave as color bar
                pass

            p.restore()


class RoomLabDayView(QWidget):
    """View schedules by room/lab vs day with navigation between schedules."""
    def __init__(self, schedules: List[List[object]], parent=None, initial_index: int | None = None, 
                 initial_filter: str = "all", initial_item_index: int = 0):
        super().__init__(parent)
        self.setWindowTitle("Schedules by Room/Lab · Day")
        self.setMinimumSize(900, 700)

        self.schedules = schedules
        self.controller = generate_controller(self.schedules)
        # Start at provided index if valid
        if initial_index is not None and 0 <= initial_index < len(self.schedules):
            try:
                # The controller exposes 'index'
                self.controller.index = initial_index
            except Exception:
                pass

        # Filter state for room/faculty view
        self.current_filter_type = initial_filter  # "all", "room", "faculty"
        self.room_list = []
        self.faculty_list = []
        self.current_room_index = initial_item_index if initial_filter == "room" else 0
        self.current_faculty_index = initial_item_index if initial_filter == "faculty" else 0

        root = QVBoxLayout(self)

        # Title
        title = QLabel("Room/Lab Day Visualization")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        root.addWidget(title)

        # Filter and Nav bar
        control_layout = QHBoxLayout()
        
        # Filter dropdown
        filter_label = QLabel("Filter by:")
        filter_label.setFont(QFont("Arial", 10))
        control_layout.addWidget(filter_label)
        
        self.filter_selector = QComboBox()
        self.filter_selector.addItems(['All Locations', 'By Room', 'By Faculty'])
        self.filter_selector.setFont(QFont("Arial", 10))
        self.filter_selector.setMinimumWidth(120)
        self.filter_selector.currentTextChanged.connect(self.on_filter_changed)
        control_layout.addWidget(self.filter_selector)
        
        # Set initial filter state
        if initial_filter == "room":
            self.filter_selector.setCurrentText('By Room')
        elif initial_filter == "faculty":
            self.filter_selector.setCurrentText('By Faculty')
        else:
            self.filter_selector.setCurrentText('All Locations')
        
        # Item selector (for room/faculty navigation)
        self.item_selector = QComboBox()
        self.item_selector.setFont(QFont("Arial", 10))
        self.item_selector.setMinimumWidth(150)
        self.item_selector.currentIndexChanged.connect(self.on_item_changed)
        self.item_selector.hide()  # Hidden initially
        control_layout.addWidget(self.item_selector)
        
        control_layout.addStretch(1)

        # Schedule navigation
        self.prev_btn = QPushButton("← Prev")
        self.next_btn = QPushButton("Next →")
        self.page = QLabel("")
        self.page.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(self.prev_btn)
        control_layout.addWidget(self.page)
        control_layout.addWidget(self.next_btn)
        
        root.addLayout(control_layout)

        # Scrollable panels
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        root.addWidget(self.scroll, 1)
        self.container = QWidget()
        self.scroll.setWidget(self.container)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignTop)

        self.prev_btn.clicked.connect(self.prev_schedule)
        self.next_btn.clicked.connect(self.next_schedule)

        # Initialize filter state and render
        if self.current_filter_type == "room":
            self.populate_room_list()
            self.item_selector.show()
        elif self.current_filter_type == "faculty":
            self.populate_faculty_list()
            self.item_selector.show()
        
        self.render_current()

    def _schedule_to_csv_list(self, schedule) -> List[str]:
        # schedule may be course objects with as_csv(), or strings already
        out = []
        for item in schedule:
            if item is None:
                continue
            if hasattr(item, "as_csv"):
                try:
                    out.append(item.as_csv())
                except Exception:
                    pass
            elif isinstance(item, str):
                out.append(item)
            else:
                # try to build from attributes if present
                # fallback: skip
                pass
        return out

    def prev_schedule(self):
        if not self.schedules:
            return
        self.controller.previous_schedule()
        self.render_current()

    def next_schedule(self):
        if not self.schedules:
            return
        self.controller.next_schedule()
        self.render_current()

    def clear_panels(self):
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

    def on_filter_changed(self, filter_text):
        """Handle filter selector changes"""
        if filter_text == 'All Locations':
            self.current_filter_type = "all"
            self.item_selector.hide()
        elif filter_text == 'By Room':
            self.current_filter_type = "room"
            self.populate_room_list()
            self.item_selector.show()
        elif filter_text == 'By Faculty':
            self.current_filter_type = "faculty"
            self.populate_faculty_list()
            self.item_selector.show()
        self.render_current()

    def on_item_changed(self, index):
        """Handle item selector changes"""
        if index < 0:
            return
        if self.current_filter_type == "room":
            self.current_room_index = index
        elif self.current_filter_type == "faculty":
            self.current_faculty_index = index
        self.render_current()

    def populate_room_list(self):
        """Populate room list for current schedule"""
        by_loc = self.controller.get_room_day_blocks()
        self.room_list = sorted(by_loc.keys())
        
        self.item_selector.blockSignals(True)
        self.item_selector.clear()
        for i, room in enumerate(self.room_list):
            self.item_selector.addItem(f"{i + 1}. {room}")
        if self.current_room_index < len(self.room_list):
            self.item_selector.setCurrentIndex(self.current_room_index)
        else:
            self.current_room_index = 0
            self.item_selector.setCurrentIndex(0)
        self.item_selector.blockSignals(False)

    def populate_faculty_list(self):
        """Populate faculty list for current schedule"""
        csv_list = self.controller.get_current_schedule_strings()
        faculty_set = set()
        
        from src.views.cli.schedules_view import parse_course_string
        for csv_line in csv_list:
            course = parse_course_string(csv_line)
            if course:
                faculty_set.add(course["faculty"])
        
        self.faculty_list = sorted(faculty_set)
        
        self.item_selector.blockSignals(True)
        self.item_selector.clear()
        for i, faculty in enumerate(self.faculty_list):
            self.item_selector.addItem(f"{i + 1}. {faculty}")
        if self.current_faculty_index < len(self.faculty_list):
            self.item_selector.setCurrentIndex(self.current_faculty_index)
        else:
            self.current_faculty_index = 0
            self.item_selector.setCurrentIndex(0)
        self.item_selector.blockSignals(False)

    def render_current(self):
        self.clear_panels()
        total = len(self.schedules)
        idx = self.controller.index if total else -1
        if idx < 0 or total == 0:
            self.page.setText("No schedules")
            return
        self.page.setText(f"Schedule {idx + 1} of {total}")

        by_loc = self.controller.get_room_day_blocks()

        if self.current_filter_type == "all":
            # Show all locations
            for loc in sorted(by_loc.keys()):
                panel = RoomPanel(loc, by_loc[loc], self)
                self.container_layout.addWidget(panel)
        elif self.current_filter_type == "room":
            # Show only selected room
            if self.room_list and self.current_room_index < len(self.room_list):
                room = self.room_list[self.current_room_index]
                if room in by_loc:
                    panel = RoomPanel(room, by_loc[room], self)
                    self.container_layout.addWidget(panel)
        elif self.current_filter_type == "faculty":
            # Show rooms that have courses taught by selected faculty
            if self.faculty_list and self.current_faculty_index < len(self.faculty_list):
                faculty = self.faculty_list[self.current_faculty_index]
                for loc in sorted(by_loc.keys()):
                    # Filter blocks to only show those with the selected faculty
                    filtered_blocks = [b for b in by_loc[loc] if b.faculty == faculty]
                    if filtered_blocks:
                        panel = RoomPanel(f"{loc} - {faculty}", filtered_blocks, self)
                        self.container_layout.addWidget(panel)
        
        self.container_layout.addStretch()
