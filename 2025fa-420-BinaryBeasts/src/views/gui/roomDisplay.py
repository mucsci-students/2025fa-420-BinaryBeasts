from __future__ import annotations

from typing import List, Dict, Any
import os
import sys
# Ensure Python can resolve the top-level 'src' package when running this file directly
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# Use scheduler models for days/times
from scheduler.models.day import Day
from scheduler.models.time_slot import TimeInstance, TimeSlot
from scheduler.models.course import CourseInstance, Course
# GUI keeps its own navigation state to avoid CLI prints


WEEKDAYS = [Day.MON, Day.TUE, Day.WED, Day.THU, Day.FRI]


def times_to_day_columns_models(times: List[TimeInstance], lab_index: int | None = None, mark_lab: bool = False) -> Dict[str, List[str]]:
    """Map TimeInstance models to day name -> list of time ranges strings using scheduler's types.

    When lab_index is provided and mark_lab is True, prefix the corresponding time with '^'.
    """
    cols: Dict[str, List[str]] = {d.name: [] for d in WEEKDAYS}
    for idx, t in enumerate(times):
        day_name = t.day.name
        start_str = str(t.start)  # TimePoint -> "HH:MM"
        stop_str = str(t.stop)    # computed property -> TimePoint
        s = f"{start_str}-{stop_str}"
        if mark_lab and lab_index is not None and idx == lab_index:
            s = f"^{s}"
        cols.setdefault(day_name, []).append(s)
    return {d.name: cols.get(d.name, []) for d in WEEKDAYS}


def group_by_room(schedule: List[CourseInstance] | List[Dict[str, Any]]) -> Dict[str, List[Any]]:
    grouped: Dict[str, List[Any]] = {}
    for inst in schedule:
        if isinstance(inst, CourseInstance):
            room = inst.room or "Unassigned"
        else:
            room = inst.get("room") or "Unassigned"
        grouped.setdefault(room, []).append(inst)
    return grouped


class RoomDisplay(QWidget):
    """Display generated schedules grouped by room with navigation between schedules.

    Expected input (primary):
    - schedules: List[List[CourseInstance]] as produced by `Scheduler.get_models()`
      in `main_controller.generate_schedules`. Each inner list is a single schedule,
      containing CourseInstance objects for that schedule.

    Also supported (fallback):
    - schedules: List[List[dict]] in the JSON shape from the scheduler JSON writer
      (keys: course, faculty, room, lab, times[{day,start,duration}], lab_index?).
    """

    def __init__(self, schedules: List[List[CourseInstance]] | List[List[Dict[str, Any]]]):
        super().__init__()
        self.setWindowTitle("College Course Scheduler - Room View")
        self.setMinimumSize(900, 600)
        self.schedules = schedules
        # Local navigation index (avoid CLI controller side-effects/prints)
        self.index = 0 if schedules else -1

        root = QVBoxLayout(self)

        title = QLabel("Room Schedule Display")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        root.addWidget(title)

        # Navigation
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("← Prev")
        self.next_btn = QPushButton("Next →")
        for b in (self.prev_btn, self.next_btn):
            b.setFont(QFont("Arial", 9))
            b.setStyleSheet("padding: 8px; background-color: #4CAF50; color: white; border-radius: 5px;")
        self.page_label = QLabel("")
        self.page_label.setAlignment(Qt.AlignCenter)
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.page_label, 1)
        nav_layout.addWidget(self.next_btn)
        root.addLayout(nav_layout)

        # Scrollable content area
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

    @staticmethod
    def from_iterable(results: List[List[CourseInstance]] | List[List[Dict[str, Any]]] | Any) -> "RoomDisplay":
        """Convenience constructor when you have an iterable/generator of schedules.

        Example:
            scheduler = Scheduler(config)
            display = RoomDisplay.from_iterable(scheduler.get_models())
        """
        try:
            schedules_list = list(results)
        except TypeError:
            # Not iterable; assume already a list
            schedules_list = results  # type: ignore[assignment]
        return RoomDisplay(schedules_list)

    def prev_schedule(self) -> None:
        if self.schedules:
            self.index = (self.index - 1) % len(self.schedules)
            self.render_current()

    def next_schedule(self) -> None:
        if self.schedules:
            self.index = (self.index + 1) % len(self.schedules)
            self.render_current()

    def clear_container(self) -> None:
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

    def render_current(self) -> None:
        self.clear_container()
        total = len(self.schedules)
        if self.index < 0 or total == 0:
            self.page_label.setText("No schedules to display")
            return
        self.page_label.setText(f"Schedule {self.index + 1} of {total}")

        schedule = self.schedules[self.index]
        groups = group_by_room(schedule)

        for room_name, items in groups.items():
            self.container_layout.addWidget(self._build_room_block(room_name, items))

        self.container_layout.addStretch()

    def _build_room_block(self, room_name: str, items: List[Any]) -> QWidget:
        block = QWidget()
        v = QVBoxLayout(block)

        header = QLabel(room_name)
        header.setFont(QFont("Arial", 14, QFont.Bold))
        v.addWidget(header)

        # Table header similar to CUI
        header_row = self._build_row(["Course", "Faculty (Lab)"] + [d.name for d in WEEKDAYS], bold=True)
        v.addWidget(header_row)

        # Content rows
        for inst in items:
            if isinstance(inst, CourseInstance):
                course_str = str(inst.course)
                faculty = inst.faculty or ""
                lab = inst.lab or None
                fac_lab = f"{faculty} ({lab})" if lab else faculty
                # Do not mark caret in GUI display
                day_cols = times_to_day_columns_models(inst.times, lab_index=inst.lab_index, mark_lab=False)
                cells = [course_str, fac_lab] + ["; ".join(day_cols.get(d.name, [])) for d in WEEKDAYS]
            else:
                course_str = inst.get("course", "")
                faculty = inst.get("faculty") or ""
                lab = inst.get("lab") or None
                fac_lab = f"{faculty} ({lab})" if lab else faculty
                # fallback: if raw JSON-like dicts are provided, we try to adapt
                times_list = inst.get("times", [])
                lab_idx = inst.get("lab_index")
                # Map dicts to pseudo TimeInstance-like formatting
                cols: Dict[str, List[str]] = {d.name: [] for d in WEEKDAYS}
                for idx, t in enumerate(times_list):
                    day_name = Day(t.get("day", 1)).name if isinstance(t.get("day"), int) else str(t.get("day", "MON"))
                    start = t.get("start", 0)
                    dur = t.get("duration", 0)
                    start_str = f"{start // 60:02d}:{start % 60:02d}"
                    stop = start + dur
                    stop_str = f"{stop // 60:02d}:{stop % 60:02d}"
                    s = f"{start_str}-{stop_str}"
                    # Do not mark caret in GUI display
                    cols.setdefault(day_name, []).append(s)
                day_cols = cols
                cells = [course_str, fac_lab] + ["; ".join(day_cols.get(d.name, [])) for d in WEEKDAYS]
            v.addWidget(self._build_row(cells))

        return block

    def _build_row(self, cells: List[str], bold: bool = False) -> QWidget:
        row = QWidget()
        h = QHBoxLayout(row)
        h.setSpacing(8)
        fonts = QFont("Courier New", 9, QFont.Bold if bold else QFont.Normal)

        # Fixed column widths to keep a table-like look
        widths = [150, 180, 120, 120, 120, 120, 120]
        for i, text in enumerate(cells):
            lbl = QLabel(text)
            lbl.setFont(fonts)
            lbl.setStyleSheet("border: 1px solid #ddd; padding: 4px;")
            if i < len(widths):
                lbl.setMinimumWidth(widths[i])
                lbl.setMaximumWidth(widths[i])
            lbl.setWordWrap(True)
            h.addWidget(lbl)
        h.addStretch()
        return row


if __name__ == "__main__":
    # Minimal demo mirroring FacultyDisplay but grouped by rooms
    import sys
    from PyQt5.QtWidgets import QApplication
    from scheduler.models.time_slot import TimePoint, Duration

    def make_times(entries: List[tuple[Day, int, int]]) -> List[TimeInstance]:
        out: List[TimeInstance] = []
        for (day, start_min, dur_min) in entries:
            out.append(TimeInstance(day=day, start=TimePoint(timepoint=start_min), duration=Duration(duration=dur_min)))
        return out

    hardy140_01 = CourseInstance(
        course=Course(course_id="CMSC 140", credits=3, section=1, labs=[], rooms=[], conflicts=[], faculties=[]),
        time=TimeSlot(times=make_times([(Day.MON, 8*60, 50), (Day.WED, 8*60, 110), (Day.FRI, 8*60, 50)]), lab_index=None),
        faculty="Hardy",
        room="Roddy 147",
        lab=None,
    )
    hardy140_02 = CourseInstance(
        course=Course(course_id="CMSC 140", credits=3, section=2, labs=[], rooms=[], conflicts=[], faculties=[]),
        time=TimeSlot(times=make_times([(Day.MON, 9*60, 50), (Day.TUE, 8*60, 110), (Day.FRI, 9*60, 50)]), lab_index=None),
        faculty="Hardy",
        room="Roddy 147",
        lab=None,
    )
    zoppetti161_01 = CourseInstance(
        course=Course(course_id="CMSC 161", credits=3, section=1, labs=[], rooms=[], conflicts=[], faculties=[]),
        time=TimeSlot(times=make_times([(Day.MON, 11*60, 50), (Day.THU, 10*60, 110), (Day.FRI, 11*60, 50)]), lab_index=1),
        faculty="Zoppetti",
        room="Roddy 147",
        lab="Linux",
    )

    demo_schedules: List[List[CourseInstance]] = [
        [hardy140_01, hardy140_02, zoppetti161_01],
    ]

    app = QApplication(sys.argv)
    w = RoomDisplay(demo_schedules)
    w.show()
    sys.exit(app.exec_())
