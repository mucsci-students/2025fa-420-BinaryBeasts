import os
import pytest
from unittest.mock import MagicMock, patch
from PyQt5.QtWidgets import QApplication, QDialog, QMessageBox
from src.models.time_slot_model import TimeSlotManager
from src.controllers.time_slot_controller import TimeSlotController
from src.views.gui.timeslot_gui import (
    TimeSlotsDialog,
    DailyTimeSlotDialog,
    ClassPatternDialog,
)

# Fixture for QApplication
@pytest.fixture(scope="session")
def qapp():
    """Fixture for creating a QApplication instance."""
    # Ensure headless CI can construct Qt widgets
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

# Fixture for a mock CombinedConfig
@pytest.fixture
def mock_combined_config():
    """Fixture for a mock CombinedConfig object."""
    config = MagicMock()
    config.get_time_slots.return_value = ([], [])
    return config

# Fixture for TimeSlotManager
@pytest.fixture
def timeslot_manager(mock_combined_config):
    """Fixture for TimeSlotManager."""
    return TimeSlotManager(mock_combined_config)

# Fixture for TimeSlotController
@pytest.fixture
def timeslot_controller(timeslot_manager):
    """Fixture for TimeSlotController."""
    return TimeSlotController(timeslot_manager)

# Fixture for TimeSlotsDialog
@pytest.fixture
def timeslots_dialog(timeslot_controller, mock_combined_config):
    """Fixture for TimeSlotsDialog."""
    dialog = TimeSlotsDialog(timeslot_controller, mock_combined_config)
    return dialog

class TestTimeSlotManager:
    def test_add_daily_time_slot(self, timeslot_manager):
        assert timeslot_manager.add_daily_time_slot("MON", "08:00", "10:00", 60) is True
        assert len(timeslot_manager.daily_times["MON"]) == 1
        assert timeslot_manager.daily_times["MON"][0] == {"start": "08:00", "end": "10:00", "spacing": 60}

    def test_conflicting_daily_time_slot(self, timeslot_manager):
        assert timeslot_manager.add_daily_time_slot("MON", "08:00", "10:00", 60) is True
        # Overlaps with existing 08:00-10:00
        assert timeslot_manager.add_daily_time_slot("MON", "09:00", "11:00", 30) is False

    def test_invalid_time_format_raises(self, timeslot_manager):
        with pytest.raises(ValueError):
            timeslot_manager.add_daily_time_slot("MON", "8am", "10:00", 60)

    def test_delete_daily_time_slot(self, timeslot_manager):
        timeslot_manager.add_daily_time_slot("MON", "08:00", "10:00", 60)
        assert timeslot_manager.delete_daily_time_slot("MON", 0) is True
        assert len(timeslot_manager.daily_times["MON"]) == 0

    def test_add_class_pattern(self, timeslot_manager):
        assert timeslot_manager.add_class_pattern(3, [{"day": "MON", "duration": 50}]) is True
        assert len(timeslot_manager.class_patterns) == 1
        assert timeslot_manager.class_patterns[0]["credits"] == 3

    def test_update_class_pattern(self, timeslot_manager):
        timeslot_manager.add_class_pattern(3, [{"day": "MON", "duration": 50}])
        assert timeslot_manager.update_class_pattern(0, 4, [{"day": "TUE", "duration": 75}]) is True
        assert timeslot_manager.class_patterns[0]["credits"] == 4
        assert timeslot_manager.class_patterns[0]["meetings"][0]["day"] == "TUE"

    def test_delete_class_pattern(self, timeslot_manager):
        timeslot_manager.add_class_pattern(3, [{"day": "MON", "duration": 50}])
        assert timeslot_manager.delete_class_pattern(0) is True
        assert len(timeslot_manager.class_patterns) == 0

    def test_to_config_dict(self, timeslot_manager):
        timeslot_manager.add_daily_time_slot("MON", "08:00", "10:00", 60)
        timeslot_manager.add_class_pattern(3, [{"day": "MON", "duration": 50}])
        config_dict = timeslot_manager.to_config_dict()
        assert "times" in config_dict
        assert "classes" in config_dict
        assert len(config_dict["times"]["MON"]) == 1
        assert len(config_dict["classes"]) == 1

    def test_invalid_day_raises(self, timeslot_manager):
        with pytest.raises(ValueError):
            timeslot_manager.add_daily_time_slot("SAT", "08:00", "09:00", 60)

    def test_time_conflict_boundaries(self, timeslot_manager):
        # Base slot
        assert timeslot_manager.add_daily_time_slot("MON", "08:00", "10:00", 60) is True
        # Touching end/start boundaries should not conflict
        assert timeslot_manager.add_daily_time_slot("MON", "10:00", "12:00", 60) is True
        assert timeslot_manager.add_daily_time_slot("MON", "06:00", "08:00", 60) is True
        # Overlapping ranges should fail
        assert timeslot_manager.add_daily_time_slot("MON", "09:00", "10:30", 60) is False
        assert timeslot_manager.add_daily_time_slot("MON", "08:00", "09:00", 60) is False

    def test_delete_invalid_index_returns_false(self, timeslot_manager):
        timeslot_manager.add_daily_time_slot("MON", "08:00", "09:00", 60)
        assert timeslot_manager.delete_daily_time_slot("MON", 99) is False

    def test_add_class_pattern_optional_fields(self, timeslot_manager):
        ok = timeslot_manager.add_class_pattern(
            4,
            [{"day": "TUE", "duration": 75, "lab": True}],
            disabled=True,
            start_time="09:30",
        )
        assert ok is True
        pat = timeslot_manager.class_patterns[-1]
        assert pat["credits"] == 4
        assert pat["meetings"][0]["lab"] is True
        assert pat["disabled"] is True
        assert pat["start_time"] == "09:30"

    def test_update_class_pattern_optional_fields_and_invalid_index(self, timeslot_manager):
        timeslot_manager.add_class_pattern(3, [{"day": "MON", "duration": 50}])
        # invalid index
        assert timeslot_manager.update_class_pattern(9, credits=5) is False
        # toggle disabled and set start_time
        assert timeslot_manager.update_class_pattern(
            0,
            credits=5,
            meetings=[{"day": "FRI", "duration": 110, "lab": False}],
            disabled=False,
            start_time="13:00",
        ) is True
        pat = timeslot_manager.class_patterns[0]
        assert pat["credits"] == 5
        assert pat["meetings"][0]["day"] == "FRI"
        assert pat.get("disabled", False) is False
        assert pat["start_time"] == "13:00"

    def test_save_config_success_and_failure(self, tmp_path, timeslot_manager):
        # success path
        cfg = {"alpha": 1}
        slots = timeslot_manager.to_config_dict()
        p = tmp_path / "out.json"
        ok = timeslot_manager.save_config(cfg, slots, str(p))
        assert ok is True and p.exists()

        # failure path (directory doesn't exist)
        bad_path = tmp_path / "missing" / "sub" / "x.json"
        assert timeslot_manager.save_config(cfg, slots, str(bad_path)) is False

    def test_load_time_slots_from_attribute_and_dict_configs(self):
        # Build attribute-style config
        class Slot:
            def __init__(self, start, end, spacing=None):
                self.start = start
                self.end = end
                if spacing is not None:
                    self.spacing = spacing

        class Times:
            def __init__(self):
                self.MON = [Slot("08:00", "10:00", 60)]
                self.TUE = []
                self.WED = []
                self.THU = []
                self.FRI = []

        class Meeting:
            def __init__(self, day, duration, lab=False):
                self.day = day
                self.duration = duration
                self.lab = lab

        class Cls:
            def __init__(self):
                self.credits = 3
                self.disabled = True
                self.start_time = "09:00"
                self.meetings = [Meeting("MON", 50, lab=True)]

        class TSCfg:
            def __init__(self):
                self.times = Times()
                self.classes = [Cls()]

        class Cfg:
            def __init__(self):
                self.time_slot_config = TSCfg()

        mgr = TimeSlotManager()
        mgr.load_time_slots(Cfg())  # type: ignore[arg-type]
        assert mgr.daily_times["MON"][0]["spacing"] == 60
        assert mgr.class_patterns[0]["disabled"] is True
        assert mgr.class_patterns[0]["meetings"][0]["lab"] is True

        # Now dict-style times (no attributes) branch; values must still be slot-like objects
        class S:
            def __init__(self, start, end, spacing=None):
                self.start = start
                self.end = end
                if spacing is not None:
                    self.spacing = spacing
        times_dict = {"MON": [S("10:00", "11:00", 30)]}

        class DictTimesCfg:
            def __init__(self):
                class TS:
                    def __init__(self):
                        self.times = times_dict
                        self.classes = []
                self.time_slot_config = TS()

        mgr.load_time_slots(DictTimesCfg())  # type: ignore[arg-type]
        assert mgr.daily_times["MON"][0]["start"] == "10:00"

class TestTimeSlotController:
    def test_add_daily_time_slot(self, timeslot_controller):
        assert timeslot_controller.add_daily_time_slot("MON", "10:00", "12:00", 30) is True
        slots = timeslot_controller.get_daily_times()
        assert len(slots["MON"]) == 1
        slot = slots["MON"][0]
        assert slot["start"] == "10:00"
        assert slot["end"] == "12:00"
        assert slot.get("spacing") == 30

    def test_update_daily_time_slot(self, timeslot_controller):
        timeslot_controller.add_daily_time_slot("MON", "10:00", "12:00", 30)
        assert timeslot_controller.update_daily_time_slot("MON", 0, "11:00", "13:00", 60) is True
        slot = timeslot_controller.get_daily_times()["MON"][0]
        assert slot["start"] == "11:00"
        assert slot["end"] == "13:00"
        assert slot.get("spacing") == 60

    def test_delete_daily_time_slot(self, timeslot_controller):
        timeslot_controller.add_daily_time_slot("MON", "10:00", "12:00", 30)
        assert timeslot_controller.delete_daily_time_slot("MON", 0) is True
        assert len(timeslot_controller.get_daily_times()["MON"]) == 0

    def test_add_class_pattern(self, timeslot_controller):
        assert timeslot_controller.add_class_pattern(3, [{"day": "WED", "duration": 50}]) is True
        patterns = timeslot_controller.get_class_patterns()
        assert len(patterns) == 1
        pattern = patterns[0]
        assert pattern["credits"] == 3
        assert pattern["meetings"][0]["day"] == "WED"

    def test_update_class_pattern(self, timeslot_controller):
        timeslot_controller.add_class_pattern(3, [{"day": "WED", "duration": 50}])
        assert timeslot_controller.update_class_pattern(0, 4, [{"day": "THU", "duration": 75}]) is True
        pattern = timeslot_controller.get_class_patterns()[0]
        assert pattern["credits"] == 4
        assert pattern["meetings"][0]["day"] == "THU"

    def test_delete_class_pattern(self, timeslot_controller):
        timeslot_controller.add_class_pattern(3, [{"day": "WED", "duration": 50}])
        assert timeslot_controller.delete_class_pattern(0) is True
        assert len(timeslot_controller.get_class_patterns()) == 0

    def test_validate_time_format(self, timeslot_controller):
        assert timeslot_controller.validate_time_format("12:30") is True
        assert timeslot_controller.validate_time_format("12:60") is False
        assert timeslot_controller.validate_time_format("25:00") is False
        assert timeslot_controller.validate_time_format("abc") is False

    def test_update_daily_time_slot_invalid_time_raises(self, timeslot_controller):
        timeslot_controller.add_daily_time_slot("MON", "08:00", "09:00")
        with pytest.raises(ValueError):
            timeslot_controller.update_daily_time_slot("MON", 0, "bad", "09:00")

    def test_save_to_file_true_and_false(self, tmp_path, timeslot_controller):
        cfg = {"ok": True}
        slots = timeslot_controller.mgr.to_config_dict()
        good = tmp_path / "x.json"
        assert timeslot_controller.save_to_file(cfg, slots, str(good)) is True
        bad = tmp_path / "missing" / "sub" / "y.json"
        assert timeslot_controller.save_to_file(cfg, slots, str(bad)) is False

    def test_add_daily_time_slot_invalid_time_raises(self, timeslot_controller):
        with pytest.raises(ValueError):
            timeslot_controller.add_daily_time_slot("MON", "8am", "09:00")

    def test_update_delete_invalid_indices(self, timeslot_controller):
        # nothing exists yet; invalid indexes should be False, not raise
        assert timeslot_controller.update_daily_time_slot("MON", 0, "08:00", "09:00") is False
        assert timeslot_controller.delete_daily_time_slot("MON", 0) is False

    def test_get_daily_times_for_unknown_day(self, timeslot_controller):
        assert timeslot_controller.get_daily_times_for_day("SAT") == []

    def test_save_to_combined_config_success_and_failure(self, timeslot_controller):
        # Prepare some data so loop runs
        timeslot_controller.add_daily_time_slot("MON", "08:00", "09:00", 60)

        class Times:
            def __init__(self):
                # expose MON..FRI as attributes so hasattr is True
                self.MON = []
                self.TUE = []
                self.WED = []
                self.THU = []
                self.FRI = []

        class TimeSlotConfig:
            def __init__(self):
                self.times = Times()

        class Editable:
            def __init__(self):
                self.time_slot_config = TimeSlotConfig()

        class GoodCombined:
            def __init__(self):
                self._editable = Editable()

            def edit_mode(self):
                class Ctx:
                    def __init__(self, e):
                        self.e = e
                    def __enter__(self):
                        return self.e
                    def __exit__(self, exc_type, exc, tb):
                        return False
                return Ctx(self._editable)

        assert timeslot_controller.save_to_combined_config(GoodCombined()) is True

        class BadCombined(GoodCombined):
            def edit_mode(self):
                raise RuntimeError("boom")

        assert timeslot_controller.save_to_combined_config(BadCombined()) is False
class TestTimeSlotsDialog:
    def test_dialog_creation(self, timeslots_dialog):
        """Test that the timeslots dialog initializes correctly."""
        assert timeslots_dialog is not None
        assert timeslots_dialog.windowTitle() == "Scheduler - Time Slot Manager"

    def test_add_daily_slot(self, timeslots_dialog, timeslot_controller):
        """Test adding a daily time slot through the GUI."""
        def fake_exec(self):
            self.result_data = {"day": "MON", "start": "08:00", "end": "10:00", "spacing": 60}
            return QDialog.Accepted

        with patch.object(DailyTimeSlotDialog, 'exec_', fake_exec):
            timeslots_dialog.add_daily_time_slot()

        assert len(timeslot_controller.get_daily_times()["MON"]) == 1
        assert timeslots_dialog.daily_times_list.count() == 1

    def test_edit_daily_slot(self, timeslots_dialog, timeslot_controller):
        """Test editing a daily time slot through the GUI."""
        timeslot_controller.add_daily_time_slot("MON", "08:00", "10:00", 60)
        timeslots_dialog.refresh_daily_times()

        def fake_exec(self):
            self.result_data = {"day": "MON", "start": "09:00", "end": "11:00", "spacing": 30}
            return QDialog.Accepted

        timeslots_dialog.daily_times_list.setCurrentRow(0)
        with patch.object(DailyTimeSlotDialog, 'exec_', fake_exec):
            timeslots_dialog.edit_daily_time_slot()

        slot = timeslot_controller.get_daily_times()["MON"][0]
        assert slot["start"] == "09:00"
        assert slot["end"] == "11:00"

    def test_delete_daily_slot(self, timeslots_dialog, timeslot_controller):
        """Test deleting a daily time slot through the GUI."""
        timeslot_controller.add_daily_time_slot("MON", "08:00", "10:00", 60)
        timeslots_dialog.refresh_daily_times()

        timeslots_dialog.daily_times_list.setCurrentRow(0)
        with patch('PyQt5.QtWidgets.QMessageBox.question', return_value=QMessageBox.Yes):
            timeslots_dialog.delete_daily_time_slot()

        assert len(timeslot_controller.get_daily_times()["MON"]) == 0
        assert timeslots_dialog.daily_times_list.count() == 0

    def test_add_class_pattern(self, timeslots_dialog, timeslot_controller):
        """Test adding a class pattern through the GUI."""
        def fake_exec(self):
            self.result_data = {
                "credits": 3,
                "meetings": [{"day": "MON", "duration": 50, "lab": False}],
                "disabled": False,
            }
            return QDialog.Accepted

        with patch.object(ClassPatternDialog, 'exec_', fake_exec):
            timeslots_dialog.add_class_pattern()

        assert len(timeslot_controller.get_class_patterns()) == 1
        assert timeslots_dialog.class_patterns_list.count() == 1


def test_daily_time_slot_dialog_validation_and_accept():
    dlg = DailyTimeSlotDialog()

    # Empty inputs -> should not accept and result_data remains None
    dlg.start_input.setText("")
    dlg.end_input.setText("")
    dlg.accept()
    assert dlg.result_data is None

    # Invalid format -> still no result
    dlg.start_input.setText("8am")
    dlg.end_input.setText("10:00")
    dlg.accept()
    assert dlg.result_data is None

    # Valid inputs -> result_data populated
    dlg.start_input.setText("08:00")
    dlg.end_input.setText("10:00")
    dlg.spacing_input.setValue(45)
    dlg.accept()
    assert dlg.result_data is not None
    assert dlg.result_data["start"] == "08:00"
    assert dlg.result_data["end"] == "10:00"
    assert dlg.result_data["spacing"] == 45


def test_class_pattern_add_remove_and_accept():
    dlg = ClassPatternDialog()

    # Initially one meeting
    assert len(dlg.meeting_widgets) == 1

    # Removing the only meeting should be blocked (warning) and not remove
    widget = dlg.meeting_widgets[0]["widget"]
    dlg.remove_meeting(widget)
    assert len(dlg.meeting_widgets) == 1

    # Add another meeting with data
    dlg.add_meeting({"day": "TUE", "duration": 75, "lab": True})
    assert len(dlg.meeting_widgets) == 2

    # Invalid start_time should block accept
    dlg.start_time_input.setText("25:00")
    dlg.accept()
    assert dlg.result_data is None

    # Valid start_time, accept should populate result_data
    dlg.start_time_input.setText("09:00")
    dlg.credits_input.setValue(4)
    # mark second meeting lab checkbox
    dlg.meeting_widgets[1]["lab_checkbox"].setChecked(True)
    dlg.accept()
    assert dlg.result_data is not None
    assert dlg.result_data["credits"] == 4
    assert any(m["lab"] for m in dlg.result_data["meetings"])
    assert dlg.result_data.get("start_time") == "09:00"


class FakeController:
    def __init__(self):
        self.saved = False
        # declared for the type checker; tests will mutate this flag
        self.save_ok: bool = True

    def get_daily_times_for_day(self, day):
        return [{"start": "08:00", "end": "10:00", "spacing": 30}]

    def get_class_patterns(self):
        return [{"credits": 3, "meetings": [{"day": "MON", "duration": 50}], "disabled": False}]

    def save_to_combined_config(self, combined_config):
        return getattr(self, "save_ok", True)


def test_timeslots_dialog_refresh_spacing_and_save(monkeypatch):
    controller = FakeController()
    combined = MagicMock()

    dlg = TimeSlotsDialog(controller, combined)

    # After initialization, daily_times_list should be populated
    assert dlg.daily_times_list.count() >= 1

    # Test calculate possible start times
    times = dlg._calculate_possible_start_times("08:00", "10:00", 30)
    assert times[0] == "08:00"
    assert times[-1] == "10:00"
    assert len(times) == 5

    # Show spacing dialog: patch QDialog.exec_ to avoid blocking
    with patch.object(QDialog, "exec_", return_value=QDialog.Accepted):
        dlg.daily_times_list.setCurrentRow(0)
        dlg.show_spacing_details()

    # save_and_close: success branch
    called_info = []
    monkeypatch.setattr("src.views.gui.timeslot_gui.QMessageBox.information", lambda *a, **k: called_info.append(True))
    controller.save_ok = True
    dlg.save_and_close()
    assert called_info

    # save_and_close: warning branch
    called_warn = []
    monkeypatch.setattr("src.views.gui.timeslot_gui.QMessageBox.warning", lambda *a, **k: called_warn.append(True))
    controller.save_ok = False
    dlg.save_and_close()
    assert called_warn

    def test_edit_class_pattern(self, timeslots_dialog, timeslot_controller):
        """Test editing a class pattern through the GUI."""
        timeslot_controller.add_class_pattern(3, [{"day": "MON", "duration": 50}])
        timeslots_dialog.refresh_class_patterns()

        def fake_exec(self):
            self.result_data = {
                "credits": 4,
                "meetings": [{"day": "TUE", "duration": 75, "lab": False}],
                "disabled": False,
            }
            return QDialog.Accepted

        timeslots_dialog.class_patterns_list.setCurrentRow(0)
        with patch.object(ClassPatternDialog, 'exec_', fake_exec):
            timeslots_dialog.edit_class_pattern()

        pattern = timeslot_controller.get_class_patterns()[0]
        assert pattern["credits"] == 4
        assert pattern["meetings"][0]["day"] == "TUE"

    def test_delete_class_pattern(self, timeslots_dialog, timeslot_controller):
        """Test deleting a class pattern through the GUI."""
        timeslot_controller.add_class_pattern(3, [{"day": "MON", "duration": 50}])
        timeslots_dialog.refresh_class_patterns()

        timeslots_dialog.class_patterns_list.setCurrentRow(0)
        with patch('PyQt5.QtWidgets.QMessageBox.question', return_value=QMessageBox.Yes):
            timeslots_dialog.delete_class_pattern()

        assert len(timeslot_controller.get_class_patterns()) == 0
        assert timeslots_dialog.class_patterns_list.count() == 0

    def test_daily_times_dialog_validation(self, qapp):
        # Missing fields should warn and not set result
        dlg = DailyTimeSlotDialog()
        with patch('PyQt5.QtWidgets.QMessageBox.warning') as warn:
            dlg.accept()
            warn.assert_called()
        assert dlg.result_data is None

        # Invalid format should warn
        dlg = DailyTimeSlotDialog()
        dlg.start_input.setText("25:61")
        dlg.end_input.setText("07:00")
        with patch('PyQt5.QtWidgets.QMessageBox.warning') as warn:
            dlg.accept()
            warn.assert_called()
        assert dlg.result_data is None

        # Valid data should set result_data
        dlg = DailyTimeSlotDialog()
        dlg.start_input.setText("08:00")
        dlg.end_input.setText("09:00")
        dlg.spacing_input.setValue(45)
        with patch('PyQt5.QtWidgets.QMessageBox.warning') as warn:
            dlg.accept()
            warn.assert_not_called()
        assert dlg.result_data == {"day": "MON", "start": "08:00", "end": "09:00", "spacing": 45}

    def test_class_pattern_dialog_meeting_remove_and_validation(self, qapp):
        dlg = ClassPatternDialog()
        # Attempt to remove when only one meeting -> warning and unchanged
        only = dlg.meeting_widgets[0]["widget"]
        count_before = len(dlg.meeting_widgets)
        with patch('PyQt5.QtWidgets.QMessageBox.warning') as warn:
            dlg.remove_meeting(only)
            warn.assert_called()
        assert len(dlg.meeting_widgets) == count_before

        # Add another, then remove it successfully
        dlg.add_meeting({"day": "TUE", "duration": 75, "lab": True})
        count_before = len(dlg.meeting_widgets)
        remove_widget = dlg.meeting_widgets[-1]["widget"]
        dlg.remove_meeting(remove_widget)
        assert len(dlg.meeting_widgets) == count_before - 1

        # Invalid start_time blocks accept
        dlg.start_time_input.setText("99:99")
        with patch('PyQt5.QtWidgets.QMessageBox.warning') as warn:
            dlg.accept()
            warn.assert_called()
        assert dlg.result_data is None

        # Valid start_time and disabled flag
        dlg.start_time_input.setText("09:30")
        dlg.disabled_checkbox.setChecked(True)
        dlg.accept()
        assert dlg.result_data is not None
        assert dlg.result_data["disabled"] is True
        assert dlg.result_data["start_time"] == "09:30"

    def test_timeslots_dialog_selection_checks_and_spacing(self, timeslots_dialog, timeslot_controller):
        # No selection warnings
        with patch('PyQt5.QtWidgets.QMessageBox.warning') as warn:
            timeslots_dialog.edit_daily_time_slot()
            timeslots_dialog.delete_daily_time_slot()
            timeslots_dialog.edit_class_pattern()
            timeslots_dialog.delete_class_pattern()
            timeslots_dialog.show_spacing_details()
            assert warn.call_count >= 5

        # Add a daily slot without spacing -> default 60 should be used
        timeslot_controller.add_daily_time_slot("MON", "08:00", "10:00")
        timeslots_dialog.refresh_daily_times()
        timeslots_dialog.daily_times_list.setCurrentRow(0)

        captured = {}
        def capture_spacing(day, slot, start_times):
            captured["day"] = day
            captured["slot"] = slot
            captured["start_times"] = start_times

        with patch.object(TimeSlotsDialog, '_show_spacing_dialog', side_effect=capture_spacing):
            timeslots_dialog.show_spacing_details()

        assert captured["day"] == "MON"
        assert captured["slot"]["start"] == "08:00"
        # Should step by 60 minutes by default
        assert captured["start_times"][0] == "08:00"
        assert captured["start_times"][1] == "09:00"

        # Delete flow where user selects No should not delete
        timeslots_dialog.daily_times_list.setCurrentRow(0)
        before = timeslots_dialog.daily_times_list.count()
        with patch('PyQt5.QtWidgets.QMessageBox.question', return_value=QMessageBox.No):
            timeslots_dialog.delete_daily_time_slot()
        assert timeslots_dialog.daily_times_list.count() == before

    def test_refresh_methods_error_handling(self, timeslots_dialog):
        with patch.object(timeslots_dialog.controller, 'get_daily_times_for_day', side_effect=RuntimeError("boom")):
            with patch('PyQt5.QtWidgets.QMessageBox.critical') as crit:
                timeslots_dialog.refresh_daily_times()
                crit.assert_called()
        with patch.object(timeslots_dialog.controller, 'get_class_patterns', side_effect=RuntimeError("boom")):
            with patch('PyQt5.QtWidgets.QMessageBox.critical') as crit:
                timeslots_dialog.refresh_class_patterns()
                crit.assert_called()

    def test_add_daily_time_slot_conflict_and_cancel(self, timeslots_dialog):
        # Cancel path should not call controller
        with patch.object(DailyTimeSlotDialog, 'exec_', return_value=QDialog.Rejected):
            with patch.object(timeslots_dialog.controller, 'add_daily_time_slot') as add_mock:
                timeslots_dialog.add_daily_time_slot()
                add_mock.assert_not_called()

        # Conflict path should warn
        def fake_exec(self):
            self.result_data = {"day": "MON", "start": "08:00", "end": "09:00", "spacing": 60}
            return QDialog.Accepted
        with patch.object(DailyTimeSlotDialog, 'exec_', fake_exec):
            with patch.object(timeslots_dialog.controller, 'add_daily_time_slot', return_value=False):
                with patch('PyQt5.QtWidgets.QMessageBox.warning') as warn:
                    timeslots_dialog.add_daily_time_slot()
                    warn.assert_called()

    def test_edit_daily_time_slot_update_false(self, timeslots_dialog, timeslot_controller):
        timeslot_controller.add_daily_time_slot("MON", "08:00", "09:00", 60)
        timeslots_dialog.refresh_daily_times()
        timeslots_dialog.daily_times_list.setCurrentRow(0)
        def fake_exec(self):
            self.result_data = {"day": "MON", "start": "08:30", "end": "09:30", "spacing": 30}
            return QDialog.Accepted
        with patch.object(DailyTimeSlotDialog, 'exec_', fake_exec):
            with patch.object(timeslots_dialog.controller, 'update_daily_time_slot', return_value=False):
                with patch('PyQt5.QtWidgets.QMessageBox.warning') as warn:
                    timeslots_dialog.edit_daily_time_slot()
                    warn.assert_called()

    def test_add_class_pattern_failure_and_cancel(self, timeslots_dialog):
        with patch.object(ClassPatternDialog, 'exec_', return_value=QDialog.Rejected):
            with patch.object(timeslots_dialog.controller, 'add_class_pattern') as add_mock:
                timeslots_dialog.add_class_pattern()
                add_mock.assert_not_called()
        def fake_exec(self):
            self.result_data = {"credits": 3, "meetings": [{"day": "MON", "duration": 50}], "disabled": False}
            return QDialog.Accepted
        with patch.object(ClassPatternDialog, 'exec_', fake_exec):
            with patch.object(timeslots_dialog.controller, 'add_class_pattern', return_value=False):
                with patch('PyQt5.QtWidgets.QMessageBox.warning') as warn:
                    timeslots_dialog.add_class_pattern()
                    warn.assert_called()

    def test_edit_class_pattern_update_false(self, timeslots_dialog, timeslot_controller):
        timeslot_controller.add_class_pattern(3, [{"day": "MON", "duration": 50}])
        timeslots_dialog.refresh_class_patterns()
        timeslots_dialog.class_patterns_list.setCurrentRow(0)
        def fake_exec(self):
            self.result_data = {"credits": 4, "meetings": [{"day": "TUE", "duration": 75}], "disabled": False}
            return QDialog.Accepted
        with patch.object(ClassPatternDialog, 'exec_', fake_exec):
            with patch.object(timeslots_dialog.controller, 'update_class_pattern', return_value=False):
                with patch('PyQt5.QtWidgets.QMessageBox.warning') as warn:
                    timeslots_dialog.edit_class_pattern()
                    warn.assert_called()

    def test_delete_paths_failure_and_success(self, timeslots_dialog, timeslot_controller):
        # Daily time slot failure after confirmation
        timeslot_controller.add_daily_time_slot("MON", "07:00", "08:00", 60)
        timeslots_dialog.refresh_daily_times()
        timeslots_dialog.daily_times_list.setCurrentRow(0)
        with patch('PyQt5.QtWidgets.QMessageBox.question', return_value=QMessageBox.Yes):
            with patch.object(timeslots_dialog.controller, 'delete_daily_time_slot', return_value=False):
                with patch('PyQt5.QtWidgets.QMessageBox.warning') as warn:
                    timeslots_dialog.delete_daily_time_slot()
                    warn.assert_called()

        # Class pattern failure after confirmation
        timeslot_controller.add_class_pattern(3, [{"day": "MON", "duration": 50}])
        timeslots_dialog.refresh_class_patterns()
        timeslots_dialog.class_patterns_list.setCurrentRow(0)
        with patch('PyQt5.QtWidgets.QMessageBox.question', return_value=QMessageBox.Yes):
            with patch.object(timeslots_dialog.controller, 'delete_class_pattern', return_value=False):
                with patch('PyQt5.QtWidgets.QMessageBox.warning') as warn:
                    timeslots_dialog.delete_class_pattern()
                    warn.assert_called()

    def test_show_spacing_error_branch(self, timeslots_dialog):
        with patch.object(timeslots_dialog, 'daily_times_list') as lst:
            lst.currentRow.return_value = 0
            with patch.object(timeslots_dialog.controller, 'get_daily_times_for_day', side_effect=RuntimeError("boom")):
                with patch('PyQt5.QtWidgets.QMessageBox.warning') as warn:
                    timeslots_dialog.show_spacing_details()
                    warn.assert_called()

    def test_save_and_close_exception_path(self, timeslots_dialog):
        with patch.object(timeslots_dialog.controller, 'save_to_combined_config', side_effect=RuntimeError("boom")):
            with patch('PyQt5.QtWidgets.QMessageBox.critical') as crit:
                timeslots_dialog.save_and_close()
                crit.assert_called()

    def test_save_and_close_success_and_failure(self, timeslots_dialog):
        # Patch controller to simulate save result
        with patch.object(timeslots_dialog, 'accept') as accept_mock:
            with patch.object(timeslots_dialog.controller, 'save_to_combined_config', return_value=True):
                timeslots_dialog.save_and_close()
                accept_mock.assert_called_once()

        with patch.object(timeslots_dialog.controller, 'save_to_combined_config', return_value=False):
            with patch('PyQt5.QtWidgets.QMessageBox.warning') as warn:
                timeslots_dialog.save_and_close()
                warn.assert_called()
