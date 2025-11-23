from src.views.gui.schedule_visualization_view import ScheduleVisualizationView


class CourseStub:
    def __init__(self, course_id, faculty, room, lab, slots):
        self.course_id = course_id
        self.faculty = faculty
        self.room = room
        self.lab = lab
        self.time_slots = slots

    def as_csv(self):
        parts = [self.course_id, self.faculty, self.room, self.lab] + self.time_slots
        return ",".join(parts)


def make_schedule():
    a = CourseStub("CMSC101", "Prof A", "Room1", "None", ["MON 09:00-09:50"])
    b = CourseStub("CMSC201", "Prof B", "Room2", "Lab1", ["TUE 10:00-11:20^"])
    return [[a, b]]


def test_schedule_to_csv_list_and_navigation():
    schedules = make_schedule()
    view = ScheduleVisualizationView(schedules)

    csv_list = view._schedule_to_csv_list(schedules[0])
    assert any("CMSC101" in s for s in csv_list)

    # Navigation: next/prev should not raise and should update controller index
    start_idx = view.controller.index
    view.next_schedule()
    assert isinstance(view.controller.index, int)
    view.prev_schedule()
    assert view.controller.index == start_idx


def test_populate_and_render_room_and_faculty():
    schedules = make_schedule()
    view = ScheduleVisualizationView(schedules)

    # Populate room list and ensure item selector is filled
    view.populate_room_list()
    assert len(view.room_list) >= 1

    # Populate faculty list
    view.populate_faculty_list()
    assert isinstance(view.faculty_list, list)

    # Render room_day layout (all)
    view.current_layout_type = "room_day"
    view.current_filter_type = "all"
    view.render_current()
    # After rendering, container_layout should contain widgets (at least stretch)
    assert view.container_layout.count() >= 1

    # Render faculty_day layout
    view.current_layout_type = "faculty_day"
    view.current_filter_type = "all"
    view.render_current()
    assert view.container_layout.count() >= 1
