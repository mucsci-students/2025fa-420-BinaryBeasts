import os

from src.views.cli import schedules_view as sv


# Simple test to verify the room PDF exporter writes a real PDF file.
class CourseStub:
    def __init__(self, csv: str):
        self._csv = csv

    def as_csv(self):
        return self._csv


def test_save_room_pdf_writes_pdf(tmp_path):
    # Prepare two minimal course CSVs with different rooms
    course_a = CourseStub("CMSC 101,Smith,Room 1,Lab A,MON 09:00-09:50")
    course_b = CourseStub("CMSC 201,Jones,Room 2,None,TUE 10:00-10:50")

    out_path = tmp_path / "room_out.pdf"

    # Run exporter (should return the filename it wrote)
    written = sv.save_schedules_by_room_pdf([course_a, course_b], str(out_path))

    # Basic checks
    assert written
    assert os.path.exists(written)

    # Check PDF header
    with open(written, "rb") as fh:
        header = fh.read(5)

    assert header.startswith(b"%PDF-")