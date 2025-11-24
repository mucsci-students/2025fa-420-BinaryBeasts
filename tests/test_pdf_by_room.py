"""Comprehensive tests for room PDF export functionality."""
import os
from unittest.mock import Mock, patch
import pytest

from src.views.cli import schedules_view as sv


class CourseStub:
    """Stub course object for testing."""
    def __init__(self, csv: str):
        self._csv = csv

    def as_csv(self):
        return self._csv


# ============================================================================
# Tests for save_room_pdf_view CLI function
# ============================================================================

def test_save_room_pdf_view_default_filename():
    """Test using default filename."""
    with patch('builtins.input', return_value=''):
        result = sv.save_room_pdf_view()
        assert result == "room_schedules.pdf"


def test_save_room_pdf_view_custom_filename_without_extension():
    """Test custom filename without .pdf extension."""
    with patch('builtins.input', return_value='my_rooms'):
        result = sv.save_room_pdf_view()
        assert result == "my_rooms.pdf"


def test_save_room_pdf_view_custom_filename_with_extension():
    """Test custom filename with .pdf extension."""
    with patch('builtins.input', return_value='my_rooms.pdf'):
        result = sv.save_room_pdf_view()
        assert result == "my_rooms.pdf"


def test_save_room_pdf_view_custom_filename_with_uppercase_extension():
    """Test custom filename with uppercase .PDF extension."""
    with patch('builtins.input', return_value='my_rooms.PDF'):
        result = sv.save_room_pdf_view()
        assert result == "my_rooms.PDF"


def test_save_room_pdf_view_custom_default_name():
    """Test with custom default name parameter."""
    with patch('builtins.input', return_value=''):
        result = sv.save_room_pdf_view(default_name="custom_default.pdf")
        assert result == "custom_default.pdf"


def test_save_room_pdf_view_whitespace_input():
    """Test with whitespace input (should use default)."""
    with patch('builtins.input', return_value='   '):
        result = sv.save_room_pdf_view()
        assert result == "room_schedules.pdf"


# ============================================================================
# Tests for save_schedules_by_room_pdf function
# ============================================================================

def test_save_room_pdf_writes_pdf(tmp_path):
    """Test that a valid PDF file is created."""
    course_a = CourseStub("CMSC 101,Smith,Room 1,Lab A,MON 09:00-09:50")
    course_b = CourseStub("CMSC 201,Jones,Room 2,None,TUE 10:00-10:50")

    out_path = tmp_path / "room_out.pdf"
    written = sv.save_schedules_by_room_pdf([course_a, course_b], str(out_path))

    assert written
    assert os.path.exists(written)

    # Check PDF header
    with open(written, "rb") as fh:
        header = fh.read(5)
    assert header.startswith(b"%PDF-")


def test_save_room_pdf_empty_schedule(tmp_path):
    """Test with empty schedule."""
    out_path = tmp_path / "empty_room.pdf"
    written = sv.save_schedules_by_room_pdf([], str(out_path))

    # Should still create a PDF with "No schedule data available"
    assert written
    assert os.path.exists(written)

    with open(written, "rb") as fh:
        header = fh.read(5)
    assert header.startswith(b"%PDF-")


def test_save_room_pdf_single_course(tmp_path):
    """Test with a single course."""
    course = CourseStub("CMSC 101,Smith,Room 1,Lab A,MON 09:00-09:50,WED 09:00-09:50")

    out_path = tmp_path / "single_room.pdf"
    written = sv.save_schedules_by_room_pdf([course], str(out_path))

    assert written
    assert os.path.exists(written)
    assert os.path.getsize(written) > 0


def test_save_room_pdf_multiple_courses_same_room(tmp_path):
    """Test multiple courses in the same room."""
    course_a = CourseStub("CMSC 101,Smith,Room 1,Lab A,MON 09:00-09:50")
    course_b = CourseStub("CMSC 201,Jones,Room 1,Lab B,TUE 10:00-10:50")
    course_c = CourseStub("CMSC 301,Brown,Room 1,None,WED 11:00-11:50")

    out_path = tmp_path / "same_room.pdf"
    written = sv.save_schedules_by_room_pdf([course_a, course_b, course_c], str(out_path))

    assert written
    assert os.path.exists(written)


def test_save_room_pdf_courses_without_labs(tmp_path):
    """Test courses without labs."""
    course_a = CourseStub("CMSC 101,Smith,Room 1,None,MON 09:00-09:50")
    course_b = CourseStub("CMSC 201,Jones,Room 2,None,TUE 10:00-10:50")

    out_path = tmp_path / "no_labs.pdf"
    written = sv.save_schedules_by_room_pdf([course_a, course_b], str(out_path))

    assert written
    assert os.path.exists(written)


def test_save_room_pdf_filename_without_extension(tmp_path):
    """Test that .pdf extension is added if missing."""
    course = CourseStub("CMSC 101,Smith,Room 1,Lab A,MON 09:00-09:50")

    out_path = tmp_path / "room_output"
    written = sv.save_schedules_by_room_pdf([course], str(out_path))

    assert written.endswith('.pdf')
    assert os.path.exists(written)


def test_save_room_pdf_none_course_objects_filtered(tmp_path):
    """Test that None course objects are filtered out."""
    course_a = CourseStub("CMSC 101,Smith,Room 1,Lab A,MON 09:00-09:50")

    out_path = tmp_path / "filtered.pdf"
    written = sv.save_schedules_by_room_pdf([course_a, None, None], str(out_path))

    assert written
    assert os.path.exists(written)


def test_save_room_pdf_special_characters_in_room_names(tmp_path):
    """Test rooms with special characters."""
    course = CourseStub("CMSC 101,Smith,Room A-123,Lab A,MON 09:00-09:50")

    out_path = tmp_path / "special_chars.pdf"
    written = sv.save_schedules_by_room_pdf([course], str(out_path))

    assert written
    assert os.path.exists(written)


def test_save_room_pdf_multiple_time_slots(tmp_path):
    """Test courses with multiple time slots per day."""
    course = CourseStub("CMSC 101,Smith,Room 1,Lab A,MON 09:00-09:50,MON 14:00-14:50,WED 09:00-09:50")

    out_path = tmp_path / "multi_slots.pdf"
    written = sv.save_schedules_by_room_pdf([course], str(out_path))

    assert written
    assert os.path.exists(written)


# ============================================================================
# Tests for export_by_room_pdf GUI method
# ============================================================================

def create_mock_schedules_gui(schedules=None):
    """Helper to create a mock SchedulesGUI instance."""
    from src.views.gui.schedules_gui import SchedulesGUI
    from src.controllers.schedules_controller import generate_controller

    if schedules is None:
        schedules = []

    gui = SchedulesGUI(schedules=schedules)
    gui.controller = generate_controller(schedules)
    return gui


def test_export_by_room_pdf_no_schedules_warning():
    """Test warning when no schedules available."""
    gui = create_mock_schedules_gui(schedules=[])

    with patch('src.views.gui.schedules_gui.QMessageBox') as MockQMessageBox:
        gui.export_by_room_pdf()
        MockQMessageBox.warning.assert_called_once()


def test_export_by_room_pdf_file_dialog_cancellation():
    """Test when user cancels the file dialog."""
    course = CourseStub("CMSC 101,Smith,Room 1,Lab A,MON 09:00-09:50")
    gui = create_mock_schedules_gui(schedules=[[course]])

    # Mock QFileDialog to return empty path (user cancelled)
    with patch('src.views.gui.schedules_gui.QFileDialog') as MockDialog:
        mock_dialog = Mock()
        mock_dialog.getSaveFileName.return_value = ('', '')
        MockDialog.return_value = mock_dialog

        # Should return early without error
        gui.export_by_room_pdf()


def test_export_by_room_pdf_successful_export(tmp_path):
    """Test successful PDF export."""
    course_a = CourseStub("CMSC 101,Smith,Room 1,Lab A,MON 09:00-09:50")
    course_b = CourseStub("CMSC 201,Jones,Room 2,None,TUE 10:00-10:50")
    gui = create_mock_schedules_gui(schedules=[[course_a, course_b]])

    out_path = str(tmp_path / "test_export.pdf")

    with patch('src.views.gui.schedules_gui.QFileDialog') as MockDialog, \
         patch('src.views.gui.schedules_gui.QMessageBox') as MockMessageBox:

        # Mock file dialog to return path
        mock_dialog = Mock()
        mock_dialog.getSaveFileName.return_value = (out_path, 'PDF Files (*.pdf)')
        MockDialog.return_value = mock_dialog

        gui.export_by_room_pdf()

        # Check that success message was shown
        MockMessageBox.information.assert_called_once()

        # Verify PDF was created
        assert os.path.exists(out_path)


def test_export_by_room_pdf_exception_handling():
    """Test that exceptions are handled gracefully."""
    course = CourseStub("CMSC 101,Smith,Room 1,Lab A,MON 09:00-09:50")
    gui = create_mock_schedules_gui(schedules=[[course]])

    with patch('src.views.gui.schedules_gui.QFileDialog') as MockDialog, \
         patch('src.views.gui.schedules_gui.QMessageBox') as MockMessageBox, \
         patch('src.views.cli.schedules_view.save_schedules_by_room_pdf') as mock_save:

        # Mock file dialog
        mock_dialog = Mock()
        mock_dialog.getSaveFileName.return_value = ('/invalid/path/test.pdf', 'PDF Files (*.pdf)')
        MockDialog.return_value = mock_dialog

        # Mock save function to raise exception
        mock_save.side_effect = Exception("Test error")

        gui.export_by_room_pdf()

        # Check that error message was shown
        MockMessageBox.critical.assert_called_once()
        args = MockMessageBox.critical.call_args[0]
        assert "Error" in args[1]
        assert "Test error" in args[2]


def test_export_by_room_pdf_failed_write():
    """Test when PDF write returns empty string (failure)."""
    course = CourseStub("CMSC 101,Smith,Room 1,Lab A,MON 09:00-09:50")
    gui = create_mock_schedules_gui(schedules=[[course]])

    with patch('src.views.gui.schedules_gui.QFileDialog') as MockDialog, \
         patch('src.views.gui.schedules_gui.QMessageBox') as MockMessageBox, \
         patch('src.views.cli.schedules_view.save_schedules_by_room_pdf') as mock_save:

        # Mock file dialog
        mock_dialog = Mock()
        mock_dialog.getSaveFileName.return_value = ('/tmp/test.pdf', 'PDF Files (*.pdf)')
        MockDialog.return_value = mock_dialog

        # Mock save function to return empty string (failure)
        mock_save.return_value = ""

        gui.export_by_room_pdf()

        # Check that error message was shown
        MockMessageBox.critical.assert_called_once()
        args = MockMessageBox.critical.call_args[0]
        assert "Error" in args[1]
        assert "Failed to write room PDF" in args[2]


def test_export_by_room_pdf_uses_current_schedule_index(tmp_path):
    """Test that it uses the current schedule from controller."""
    course1 = CourseStub("CMSC 101,Smith,Room 1,Lab A,MON 09:00-09:50")
    course2 = CourseStub("CMSC 201,Jones,Room 2,None,TUE 10:00-10:50")
    course3 = CourseStub("CMSC 301,Brown,Room 3,None,WED 11:00-11:50")

    # Create multiple schedules
    gui = create_mock_schedules_gui(schedules=[[course1], [course2], [course3]])
    gui.controller.index = 1  # Set to second schedule

    out_path = str(tmp_path / "current_index.pdf")

    with patch('src.views.gui.schedules_gui.QFileDialog') as MockDialog, \
         patch('src.views.gui.schedules_gui.QMessageBox') as MockMessageBox:

        mock_dialog = Mock()
        mock_dialog.getSaveFileName.return_value = (out_path, 'PDF Files (*.pdf)')
        MockDialog.return_value = mock_dialog

        gui.export_by_room_pdf()

        # Should export successfully
        MockMessageBox.information.assert_called_once()
        assert os.path.exists(out_path)