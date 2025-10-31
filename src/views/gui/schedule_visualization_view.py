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
DAY_WIDTH = 140  # Increased for better readability
DAY_PADDING = 4  # More padding between blocks
LEFT_MARGIN = 80  # More space for time labels
TEXT_OFFSET = 50
CANVAS_PADDING = 3
MIN_BLOCK_HEIGHT = 20  # Minimum height for text readability


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
        self.setMinimumWidth(LEFT_MARGIN + 5 * DAY_WIDTH + 20)
        # Height based on minute span with better scaling
        height = (self.max_h - self.min_h) * 80 + 2 * CANVAS_PADDING + 80  # More vertical space
        self.setMinimumHeight(max(150, height))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Title with background
        title_rect = QRect(5, 5, self.width() - 10, 25)
        p.fillRect(title_rect, QColor(240, 240, 240))
        p.setPen(QPen(Qt.black))
        p.setFont(QFont("Arial", 14, QFont.Bold))
        p.drawText(title_rect, Qt.AlignCenter, self.title)

        # Day labels with better formatting
        p.setFont(QFont("Arial", 11, QFont.Bold))
        x0 = LEFT_MARGIN
        for i, label in enumerate(DAY_LABELS):
            x = x0 + i * DAY_WIDTH
            day_rect = QRect(x, 35, DAY_WIDTH - DAY_PADDING, 20)
            p.fillRect(day_rect, QColor(250, 250, 250))
            p.drawText(day_rect, Qt.AlignCenter, label)

        # Time grid lines and labels with better spacing
        y0 = 65  # More space for headers
        pen_grid = QPen(QColor(220, 220, 220))
        p.setPen(pen_grid)
        time_font = QFont("Arial", 10)
        p.setFont(time_font)
        
        for hour in range(self.min_h, self.max_h + 1):
            y = y0 + (hour - self.min_h) * 80  # More vertical space per hour
            p.drawLine(LEFT_MARGIN - 5, y, LEFT_MARGIN + 5 * DAY_WIDTH, y)
            # time text on left with better formatting
            p.setPen(QPen(Qt.black))
            if hour == 0:
                time_str = "12:00 AM"
            elif hour < 12:
                time_str = f"{hour}:00 AM"
            elif hour == 12:
                time_str = "12:00 PM"
            else:
                time_str = f"{hour - 12}:00 PM"
            
            time_rect = QRect(5, y - 10, LEFT_MARGIN - 10, 20)
            p.drawText(time_rect, Qt.AlignRight | Qt.AlignVCenter, time_str)
            p.setPen(pen_grid)

        # Draw blocks with improved formatting
        for b in self.blocks:
            x = LEFT_MARGIN + (b.day - 1) * DAY_WIDTH + DAY_PADDING
            # Convert minutes to pixels with better scaling
            y_minutes = b.start - self.min_h * 60
            y = y0 + (y_minutes * 80) // 60 + CANVAS_PADDING  # Scale to match time grid
            w = DAY_WIDTH - 2 * DAY_PADDING
            h = max(MIN_BLOCK_HEIGHT, (b.duration * 80) // 60)  # Scale duration proportionally

            rect = QRect(x, y, w, h)
            
            # Color by course id with better contrast
            color = _key_color(b.course)
            fill = QColor(color)
            if getattr(b, "is_lab", False):
                # More distinct lab coloring
                fill = QColor(max(0, color.red() - 20), min(255, color.green() + 40), max(0, color.blue() - 10))
            
            # Draw block with border
            p.fillRect(rect, fill)
            p.setPen(QPen(QColor(60, 60, 60), 1))
            p.drawRect(rect)

            # Prepare fonts with better sizing
            title_font = QFont("Arial", 10, QFont.Bold)
            info_font = QFont("Arial", 9)
            p.setFont(title_font)
            fm_title = p.fontMetrics()
            p.setFont(info_font)
            fm_info = p.fontMetrics()

            # Determine layout based on block size
            padding = 4
            line_spacing = 2
            needed_two = padding + fm_title.height() + line_spacing + fm_info.height() + padding
            needed_one = padding + fm_title.height() + padding

            # Build strings with better formatting
            title_text = b.course
            if getattr(b, "is_lab", False):
                title_text += " (Lab)"
            
            faculty_text = b.faculty
            if getattr(b, "is_lab", False) and getattr(b, "lab_name", None):
                faculty_text += f" @ {b.lab_name}"

            # Draw text with proper clipping and contrast
            p.save()
            p.setClipRect(rect.adjusted(2, 2, -2, -2))  # Clip with margin
            
            # Use white text on dark backgrounds, black on light
            text_color = Qt.white if color.lightness() < 128 else Qt.black
            p.setPen(QPen(text_color))

            if h >= needed_two and w > 40:
                # Two lines with better spacing
                p.setFont(title_font)
                title_elided = fm_title.elidedText(title_text, Qt.ElideRight, w - 8)
                p.drawText(x + padding, y + padding + fm_title.ascent(), title_elided)

                p.setFont(info_font)
                faculty_elided = fm_info.elidedText(faculty_text, Qt.ElideRight, w - 8)
                p.drawText(x + padding, y + padding + fm_title.height() + line_spacing + fm_info.ascent(), faculty_elided)
                
            elif h >= needed_one and w > 30:
                # One line: prioritize course name
                p.setFont(title_font if h > 25 else info_font)
                fm = p.fontMetrics()
                text_elided = fm.elidedText(title_text, Qt.ElideRight, w - 8)
                text_y = y + (h + fm.height()) // 2 - fm.descent()
                p.drawText(x + padding, text_y, text_elided)
            
            # If block is too small for text, just show the colored block

            p.restore()


class FacultyPanel(QWidget):
    """Canvas panel that draws one faculty member's schedule across days."""
    def __init__(self, title: str, blocks: List[TimeBlock], parent=None):
        super().__init__(parent)
        self.title = title
        self.blocks = blocks
        self.min_h, self.max_h = min_max_hours(blocks)
        
        # Group blocks by day for this faculty (not by room)
        self.days = {}
        for b in blocks:
            if b.day not in self.days:
                self.days[b.day] = []
            self.days[b.day].append(b)
        
        # Sort blocks within each day by start time
        for day_blocks in self.days.values():
            day_blocks.sort(key=lambda b: b.start)
        
        self.setMinimumWidth(LEFT_MARGIN + 5 * DAY_WIDTH + 20)  # 5 days like RoomPanel
        height = (self.max_h - self.min_h) * 80 + 2 * CANVAS_PADDING + 80  # Match RoomPanel scaling
        self.setMinimumHeight(max(150, height))

    def paintEvent(self, event):
        if not self.blocks:
            return
            
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # Title with background (consistent with RoomPanel)
        title_rect = QRect(5, 5, self.width() - 10, 25)
        p.fillRect(title_rect, QColor(240, 240, 240))
        p.setPen(QPen(Qt.black))
        p.setFont(QFont("Arial", 14, QFont.Bold))
        p.drawText(title_rect, Qt.AlignCenter, self.title)

        # Day labels (like RoomPanel structure)
        p.setFont(QFont("Arial", 10, QFont.Bold))
        x0 = LEFT_MARGIN
        for i, day_label in enumerate(DAY_LABELS):
            x = x0 + i * DAY_WIDTH
            day_rect = QRect(x, 35, DAY_WIDTH - DAY_PADDING, 20)
            p.fillRect(day_rect, QColor(250, 250, 250))
            p.drawText(day_rect, Qt.AlignCenter, day_label)

        # Time grid lines and labels (consistent with RoomPanel)
        y0 = 65
        pen_grid = QPen(QColor(220, 220, 220))
        p.setPen(pen_grid)
        time_font = QFont("Arial", 10)
        p.setFont(time_font)
        
        for hour in range(self.min_h, self.max_h + 1):
            y = y0 + (hour - self.min_h) * 80  # Match RoomPanel scaling
            p.drawLine(LEFT_MARGIN - 5, y, LEFT_MARGIN + 5 * DAY_WIDTH, y)
            # time text on left with better formatting
            p.setPen(QPen(Qt.black))
            if hour == 0:
                time_str = "12:00 AM"
            elif hour < 12:
                time_str = f"{hour}:00 AM"
            elif hour == 12:
                time_str = "12:00 PM"
            else:
                time_str = f"{hour - 12}:00 PM"
            
            time_rect = QRect(5, y - 10, LEFT_MARGIN - 10, 20)
            p.drawText(time_rect, Qt.AlignRight | Qt.AlignVCenter, time_str)
            p.setPen(pen_grid)

        # Draw blocks organized by day (not by room!)
        for b in self.blocks:
            # Calculate position: each day gets its own column
            x = LEFT_MARGIN + (b.day - 1) * DAY_WIDTH + DAY_PADDING
            # Scale time positioning to match grid
            y_minutes = b.start - self.min_h * 60
            y = y0 + (y_minutes * 80) // 60 + CANVAS_PADDING
            w = DAY_WIDTH - 2 * DAY_PADDING
            h = max(MIN_BLOCK_HEIGHT, (b.duration * 80) // 60)

            rect = QRect(x, y, w, h)
            color = _key_color(b.course)
            fill = QColor(color)
            if getattr(b, "is_lab", False):
                # Consistent lab coloring with RoomPanel
                fill = QColor(max(0, color.red() - 20), min(255, color.green() + 40), max(0, color.blue() - 10))
            
            # Draw block with border
            p.fillRect(rect, fill)
            p.setPen(QPen(QColor(60, 60, 60), 1))
            p.drawRect(rect)

            # Draw course and room text with better contrast and sizing
            if w > 20 and h > 15:  # Only draw text if there's reasonable space
                p.save()
                p.setClipRect(rect.adjusted(2, 2, -2, -2))
                
                # Choose text color based on background
                text_color = Qt.white if color.lightness() < 128 else Qt.black
                p.setPen(QPen(text_color))
                
                # Prepare fonts
                title_font = QFont("Arial", 10, QFont.Bold)
                info_font = QFont("Arial", 9)
                p.setFont(title_font)
                title_fm = p.fontMetrics()
                p.setFont(info_font)
                info_fm = p.fontMetrics()
                
                # Check if we have space for two lines (course + room)
                padding = 4
                line_spacing = 2
                needed_two = padding + title_fm.height() + line_spacing + info_fm.height() + padding
                
                # Build display strings
                course_text = b.course
                if getattr(b, "is_lab", False):
                    course_text += " (Lab)"
                
                room_text = b.room
                
                if h >= needed_two and w > 60:
                    # Two lines: course name and room
                    p.setFont(title_font)
                    course_elided = title_fm.elidedText(course_text, Qt.ElideRight, w - 8)
                    text_y1 = y + padding + title_fm.ascent()
                    p.drawText(x + padding, text_y1, course_elided)
                    
                    p.setFont(info_font)
                    room_elided = info_fm.elidedText(room_text, Qt.ElideRight, w - 8)
                    text_y2 = text_y1 + line_spacing + info_fm.height()
                    p.drawText(x + padding, text_y2, room_elided)
                else:
                    # Single line: combine course and room
                    p.setFont(info_font)
                    combined_text = f"{course_text} @ {room_text}"
                    combined_elided = info_fm.elidedText(combined_text, Qt.ElideRight, w - 8)
                    text_y = y + (h + info_fm.height()) // 2 - info_fm.descent()
                    p.drawText(x + padding, text_y, combined_elided)
                
                p.restore()


class ScheduleVisualizationView(QWidget):
    """View schedules with flexible layout options and filtering."""
    def __init__(self, schedules: List[List[object]], parent=None, initial_index: int | None = None, 
                 initial_filter: str = "all", initial_item_index: int = 0):
        super().__init__(parent)
        self.setWindowTitle("Schedule Visualization")
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
        self.current_layout_type = "room_day"  # "room_day", "faculty_day"
        self.room_list = []
        self.faculty_list = []
        self.current_room_index = initial_item_index if initial_filter == "room" else 0
        self.current_faculty_index = initial_item_index if initial_filter == "faculty" else 0

        root = QVBoxLayout(self)

        # Title
        title = QLabel("Schedule Visualization")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        root.addWidget(title)

        # Layout and Filter controls
        control_layout = QHBoxLayout()
        
        # Layout type dropdown
        layout_label = QLabel("Layout:")
        layout_label.setFont(QFont("Arial", 10))
        control_layout.addWidget(layout_label)
        
        self.layout_selector = QComboBox()
        self.layout_selector.addItems(['Room × Day', 'Faculty × Day'])
        self.layout_selector.setFont(QFont("Arial", 10))
        self.layout_selector.setMinimumWidth(120)
        self.layout_selector.currentTextChanged.connect(self.on_layout_changed)
        control_layout.addWidget(self.layout_selector)
        
        control_layout.addWidget(QLabel(" | "))  # Separator
        
        # Filter dropdown
        filter_label = QLabel("Filter:")
        filter_label.setFont(QFont("Arial", 10))
        control_layout.addWidget(filter_label)
        
        self.filter_selector = QComboBox()
        self.filter_selector.addItems(['All Locations', 'By Room', 'By Faculty'])
        self.filter_selector.setFont(QFont("Arial", 10))
        self.filter_selector.setMinimumWidth(120)
        self.filter_selector.currentTextChanged.connect(self.on_filter_changed)
        control_layout.addWidget(self.filter_selector)
        
        # Set initial filter state - this will be updated by update_filter_options
        if initial_filter == "room":
            self.current_filter_type = "room"
        elif initial_filter == "faculty":
            self.current_filter_type = "faculty"
        else:
            self.current_filter_type = "all"
        
        # Item selector (for room/faculty navigation)
        self.item_selector = QComboBox()
        self.item_selector.setFont(QFont("Arial", 10))
        self.item_selector.setMinimumWidth(150)
        self.item_selector.currentIndexChanged.connect(self.on_item_changed)
        self.item_selector.hide()  # Hidden initially
        control_layout.addWidget(self.item_selector)
        
        control_layout.addStretch(1)

        # Schedule navigation (styled to match main schedules GUI)
        self.prev_btn = QPushButton("◀ Previous")
        self.prev_btn.setFont(QFont("Arial", 14))  # Match FONT2 from main GUI
        self.prev_btn.setStyleSheet('padding: 8px 12px; background-color: #327f66; color: white; border-radius: 5px;')
        control_layout.addWidget(self.prev_btn)

        # Schedule selector dropdown (moved to navigation area)
        self.schedule_selector = QComboBox()
        self.schedule_selector.setFont(QFont("Arial", 14))  # Match FONT2 from main GUI
        self.schedule_selector.setMinimumWidth(200)  # Match jump_selector width from main GUI
        # Populate with schedule numbers
        for i in range(len(self.schedules)):
            self.schedule_selector.addItem(f"Schedule {i + 1}")
        # Set current selection
        if initial_index is not None and 0 <= initial_index < len(self.schedules):
            self.schedule_selector.setCurrentIndex(initial_index)
        else:
            self.schedule_selector.setCurrentIndex(self.controller.index)
        self.schedule_selector.currentIndexChanged.connect(self.on_schedule_changed)
        control_layout.addWidget(self.schedule_selector)
        
        self.next_btn = QPushButton("Next ▶")
        self.next_btn.setFont(QFont("Arial", 14))  # Match FONT2 from main GUI
        self.next_btn.setStyleSheet('padding: 8px 12px; background-color: #327f66; color: white; border-radius: 5px;')
        control_layout.addWidget(self.next_btn)
        
        # Page label (kept for additional info, positioned after navigation)
        self.page = QLabel("")
        self.page.setAlignment(Qt.AlignCenter)
        self.page.setFont(QFont("Arial", 10))
        control_layout.addWidget(self.page)
        
        control_layout.addStretch(1)  # Balance the left stretch for centering
        
        root.addLayout(control_layout)

        # Scrollable panels with better spacing
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; }")
        root.addWidget(self.scroll, 1)
        self.container = QWidget()
        self.scroll.setWidget(self.container)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignTop)
        self.container_layout.setSpacing(15)  # Add spacing between panels
        self.container_layout.setContentsMargins(10, 10, 10, 10)  # Add margins

        self.prev_btn.clicked.connect(self.prev_schedule)
        self.next_btn.clicked.connect(self.next_schedule)

        # Initialize filter options and render
        self.update_filter_options()
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
        self.update_schedule_selector()
        self.render_current()

    def next_schedule(self):
        if not self.schedules:
            return
        self.controller.next_schedule()
        self.update_schedule_selector()
        self.render_current()

    def update_schedule_selector(self):
        """Update the schedule selector to match the current controller index"""
        self.schedule_selector.blockSignals(True)
        self.schedule_selector.setCurrentIndex(self.controller.index)
        self.schedule_selector.blockSignals(False)

    def update_page_label(self):
        """Update the page label to show current schedule"""
        total = len(self.schedules)
        idx = self.controller.index if total else -1
        if idx < 0 or total == 0:
            self.page.setText("No schedules")
        else:
            self.page.setText(f"Schedule {idx + 1} of {total}")

    def clear_panels(self):
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

    def on_schedule_changed(self, index):
        """Handle schedule selector changes"""
        if 0 <= index < len(self.schedules):
            self.controller.index = index
            self.update_page_label()
            self.render_current()

    def on_layout_changed(self, layout_text):
        """Handle layout selector changes"""
        if layout_text == 'Room × Day':
            self.current_layout_type = "room_day"
        elif layout_text == 'Faculty × Day':
            self.current_layout_type = "faculty_day"
        
        # Reset filter to "all" when switching layouts
        self.current_filter_type = "all"
        self.item_selector.hide()
        
        # Update filter options based on layout
        self.update_filter_options()
        self.render_current()

    def update_filter_options(self):
        """Update filter dropdown options based on current layout"""
        self.filter_selector.blockSignals(True)
        
        self.filter_selector.clear()
        if self.current_layout_type == "room_day":
            self.filter_selector.addItems(['All Rooms', 'By Room', 'By Faculty'])
            # Always reset to "All" when layout changes
            self.filter_selector.setCurrentText('All Rooms')
        else:  # faculty_day
            self.filter_selector.addItems(['All Faculty', 'By Faculty', 'By Room'])
            # Always reset to "All" when layout changes
            self.filter_selector.setCurrentText('All Faculty')
        
        self.filter_selector.blockSignals(False)
        self.on_filter_changed(self.filter_selector.currentText())

    def on_filter_changed(self, filter_text):
        """Handle filter selector changes"""
        if filter_text in ['All Locations', 'All Rooms', 'All Faculty']:
            self.current_filter_type = "all"
            self.item_selector.hide()
        elif 'Room' in filter_text:
            self.current_filter_type = "room"
            self.populate_room_list()
            self.item_selector.show()
        elif 'Faculty' in filter_text:
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
        self.update_page_label()
        
        if len(self.schedules) == 0 or self.controller.index < 0:
            return

        if self.current_layout_type == "room_day":
            self.render_room_day_layout()
        else:  # faculty_day
            self.render_faculty_day_layout()
        
        self.container_layout.addStretch()

    def render_room_day_layout(self):
        """Render panels organized by room/lab vs day"""
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

    def render_faculty_day_layout(self):
        """Render panels organized by faculty vs rooms+days"""
        # Get all blocks and group by faculty
        by_loc = self.controller.get_room_day_blocks()
        all_blocks = []
        for room_blocks in by_loc.values():
            all_blocks.extend(room_blocks)
        
        # Group blocks by faculty
        by_faculty = {}
        for block in all_blocks:
            if block.faculty not in by_faculty:
                by_faculty[block.faculty] = []
            by_faculty[block.faculty].append(block)

        if self.current_filter_type == "all":
            # Show all faculty
            for faculty in sorted(by_faculty.keys()):
                panel = FacultyPanel(faculty, by_faculty[faculty], self)
                self.container_layout.addWidget(panel)
        elif self.current_filter_type == "faculty":
            # Show only selected faculty
            if self.faculty_list and self.current_faculty_index < len(self.faculty_list):
                faculty = self.faculty_list[self.current_faculty_index]
                if faculty in by_faculty:
                    panel = FacultyPanel(faculty, by_faculty[faculty], self)
                    self.container_layout.addWidget(panel)
        elif self.current_filter_type == "room":
            # Show all faculty but only courses in selected room
            if self.room_list and self.current_room_index < len(self.room_list):
                selected_room = self.room_list[self.current_room_index]
                for faculty in sorted(by_faculty.keys()):
                    # Filter blocks to only show those in the selected room
                    filtered_blocks = [b for b in by_faculty[faculty] if b.room == selected_room]
                    if filtered_blocks:
                        panel = FacultyPanel(f"{faculty} - {selected_room}", filtered_blocks, self)
                        self.container_layout.addWidget(panel)
