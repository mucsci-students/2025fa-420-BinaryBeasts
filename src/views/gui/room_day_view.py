from __future__ import annotations

from typing import List
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea
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


def _faculty_color(name: str) -> QColor:
    # Deterministic color hashed from name
    h = 0x10293847
    for ch in name:
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
            color = _faculty_color(b.faculty)
            # Slightly different tone for lab blocks
            fill = QColor(color)
            if getattr(b, "is_lab", False):
                fill = QColor(min(color.red() + 30, 255), min(color.green() + 30, 255), min(color.blue() + 30, 255))
            p.fillRect(QRect(x, y, w, h), fill)
            p.setPen(QPen(Qt.black))
            # Course title
            p.setFont(QFont("Arial", 9, QFont.Bold))
            title = b.course + (" (Lab)" if getattr(b, "is_lab", False) else "")
            p.drawText(x + 8, y + 12, title)
            # Faculty
            p.setFont(QFont("Arial", 8))
            extra = b.faculty
            if getattr(b, "is_lab", False) and getattr(b, "lab_name", None):
                extra += f" @ {b.lab_name}"
            p.drawText(x + 8, y + 24, extra)


class RoomLabDayView(QWidget):
    """View schedules by room/lab vs day with navigation between schedules."""
    def __init__(self, schedules: List[List[object]], parent=None, initial_index: int | None = None):
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

        root = QVBoxLayout(self)

        # Title
        title = QLabel("Room/Lab Day Visualization")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        root.addWidget(title)

        # Nav bar
        nav = QHBoxLayout()
        self.prev_btn = QPushButton("← Prev")
        self.next_btn = QPushButton("Next →")
        self.page = QLabel("")
        self.page.setAlignment(Qt.AlignCenter)
        nav.addWidget(self.prev_btn)
        nav.addWidget(self.page, 1)
        nav.addWidget(self.next_btn)
        root.addLayout(nav)

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

    def render_current(self):
        self.clear_panels()
        total = len(self.schedules)
        idx = self.controller.index if total else -1
        if idx < 0 or total == 0:
            self.page.setText("No schedules")
            return
        self.page.setText(f"Schedule {idx + 1} of {total}")

        schedule = self.schedules[idx]
        csv_list = self._schedule_to_csv_list(schedule)
        by_loc = schedule_to_location_blocks(csv_list)

        # Sort locations alphabetically, rooms then labs mixed
        for loc in sorted(by_loc.keys()):
            panel = RoomPanel(loc, by_loc[loc], self)
            self.container_layout.addWidget(panel)
        self.container_layout.addStretch()
