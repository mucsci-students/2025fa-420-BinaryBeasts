import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QColor, QPaintEvent
from PyQt5.QtCore import QRect, Qt

from src.views.gui.schedule_visualization_view import (
    RoomPanel,
    _key_color,
    DAY_LABELS,
    DAY_WIDTH,
    LEFT_MARGIN,
    MIN_BLOCK_HEIGHT
)
from src.models.room_day_model import TimeBlock


class TestKeyColor(unittest.TestCase):
    """Test the _key_color function."""
    
    def test_key_color_deterministic(self):
        """Test that _key_color returns consistent colors for same input."""
        color1 = _key_color("CMSC 140")
        color2 = _key_color("CMSC 140")
        
        self.assertEqual(color1.hue(), color2.hue())
        self.assertEqual(color1.saturation(), color2.saturation())
        self.assertEqual(color1.value(), color2.value())
    
    def test_key_color_different_inputs(self):
        """Test that different inputs produce different colors."""
        color1 = _key_color("CMSC 140")
        color2 = _key_color("CMSC 161")
        
        # Colors should be different (at least hue should differ)
        self.assertNotEqual(color1.hue(), color2.hue())
    
    def test_key_color_empty_string(self):
        """Test _key_color with empty string."""
        color = _key_color("")
        
        self.assertIsInstance(color, QColor)
        self.assertTrue(color.isValid())
    
    def test_key_color_special_characters(self):
        """Test _key_color with special characters."""
        color = _key_color("CMSC 140.01 Lab^")
        
        self.assertIsInstance(color, QColor)
        self.assertTrue(color.isValid())
    
    def test_key_color_range(self):
        """Test that _key_color produces valid HSV values."""
        color = _key_color("TEST")
        
        self.assertTrue(0 <= color.hue() <= 359)
        self.assertEqual(color.saturation(), 200)
        self.assertEqual(color.value(), 180)


class TestRoomPanel(unittest.TestCase):
    """Test the RoomPanel widget."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for testing GUI components."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_blocks = [
            TimeBlock(
                day=1, start=540, duration=50,  # MON 9:00-9:50
                course="CMSC 140", faculty="Hardy", room="Roddy 147"
            ),
            TimeBlock(
                day=3, start=600, duration=110,  # WED 10:00-11:50
                course="CMSC 152", faculty="Smith", room="Roddy 147",
                is_lab=True, lab_name="Mac Lab"
            ),
            TimeBlock(
                day=5, start=840, duration=50,  # FRI 14:00-14:50
                course="CMSC 161", faculty="Jones", room="Roddy 147"
            )
        ]
    
    def test_room_panel_creation(self):
        """Test basic RoomPanel creation."""
        panel = RoomPanel("Test Room", self.sample_blocks)
        
        self.assertEqual(panel.title, "Test Room")
        self.assertEqual(panel.blocks, self.sample_blocks)
        self.assertEqual(len(panel.blocks), 3)
    
    def test_room_panel_empty_blocks(self):
        """Test RoomPanel with empty blocks list."""
        panel = RoomPanel("Empty Room", [])
        
        self.assertEqual(panel.title, "Empty Room")
        self.assertEqual(panel.blocks, [])
        self.assertEqual(len(panel.blocks), 0)
    
    def test_room_panel_minimum_dimensions(self):
        """Test that RoomPanel sets appropriate minimum dimensions."""
        panel = RoomPanel("Test Room", self.sample_blocks)
        
        # Check minimum width includes space for all days plus margins
        expected_min_width = LEFT_MARGIN + 5 * DAY_WIDTH + 20
        self.assertEqual(panel.minimumWidth(), expected_min_width)
        
        # Check minimum height is reasonable
        self.assertGreater(panel.minimumHeight(), 150)
    
    def test_room_panel_time_range_calculation(self):
        """Test that RoomPanel correctly calculates time ranges."""
        panel = RoomPanel("Test Room", self.sample_blocks)
        
        # min_h and max_h should be calculated from blocks
        self.assertIsInstance(panel.min_h, int)
        self.assertIsInstance(panel.max_h, int)
        self.assertLessEqual(panel.min_h, panel.max_h)
    
    def test_room_panel_single_block(self):
        """Test RoomPanel with a single block."""
        single_block = [TimeBlock(
            day=2, start=720, duration=60,  # TUE 12:00-13:00
            course="CMSC 330", faculty="Brown", room="Test Room"
        )]
        
        panel = RoomPanel("Single Block Room", single_block)
        
        self.assertEqual(len(panel.blocks), 1)
        self.assertEqual(panel.blocks[0].course, "CMSC 330")
    
    def test_paint_event_structure(self):
        """Test that paintEvent method exists and can be set up."""
        panel = RoomPanel("Test Room", self.sample_blocks)
        
        # Verify the panel has the paintEvent method
        self.assertTrue(hasattr(panel, 'paintEvent'))
        self.assertTrue(callable(getattr(panel, 'paintEvent')))
        
        # Verify panel dimensions are calculated
        self.assertIsInstance(panel.min_h, int)
        self.assertIsInstance(panel.max_h, int)
        self.assertGreater(panel.minimumWidth(), 0)
        self.assertGreater(panel.minimumHeight(), 0)


class TestRoomPanelPainting(unittest.TestCase):
    """Test RoomPanel painting functionality in more detail."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for testing GUI components."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures."""
        self.blocks_with_labs = [
            TimeBlock(
                day=1, start=540, duration=50,  # MON 9:00-9:50
                course="CMSC 140", faculty="Hardy", room="Roddy 147"
            ),
            TimeBlock(
                day=2, start=600, duration=110,  # TUE 10:00-11:50 (Lab)
                course="CMSC 152", faculty="Smith", room="Roddy 147",
                is_lab=True, lab_name="Mac Lab"
            )
        ]
    
    def test_room_panel_with_lab_blocks(self):
        """Test RoomPanel creation with lab blocks."""
        panel = RoomPanel("Lab Room", self.blocks_with_labs)
        
        # Find the lab block
        lab_block = next(b for b in panel.blocks if b.is_lab)
        self.assertTrue(lab_block.is_lab)
        self.assertEqual(lab_block.lab_name, "Mac Lab")
        self.assertEqual(lab_block.duration, 110)
    
    def test_room_panel_block_sorting(self):
        """Test that blocks are handled in the order provided."""
        unsorted_blocks = [
            TimeBlock(day=5, start=900, duration=50, course="C", faculty="Z", room="R"),  # FRI
            TimeBlock(day=1, start=500, duration=50, course="A", faculty="X", room="R"),  # MON
            TimeBlock(day=3, start=700, duration=50, course="B", faculty="Y", room="R")   # WED
        ]
        
        panel = RoomPanel("Unsorted Room", unsorted_blocks)
        
        # Blocks should be stored as provided (RoomPanel doesn't sort them)
        self.assertEqual(panel.blocks[0].course, "C")
        self.assertEqual(panel.blocks[1].course, "A")
        self.assertEqual(panel.blocks[2].course, "B")


class TestScheduleVisualizationConstants(unittest.TestCase):
    """Test constants and configuration values."""
    
    def test_day_labels(self):
        """Test DAY_LABELS constant."""
        expected_days = ["MON", "TUE", "WED", "THU", "FRI"]
        self.assertEqual(DAY_LABELS, expected_days)
        self.assertEqual(len(DAY_LABELS), 5)
    
    def test_layout_constants(self):
        """Test layout-related constants."""
        self.assertIsInstance(DAY_WIDTH, int)
        self.assertGreater(DAY_WIDTH, 0)
        
        self.assertIsInstance(LEFT_MARGIN, int)
        self.assertGreater(LEFT_MARGIN, 0)
        
        self.assertIsInstance(MIN_BLOCK_HEIGHT, int)
        self.assertGreater(MIN_BLOCK_HEIGHT, 0)


class TestRoomPanelIntegration(unittest.TestCase):
    """Integration tests for RoomPanel with realistic data."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for testing GUI components."""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
    
    def test_full_week_schedule(self):
        """Test RoomPanel with a full week of classes."""
        full_week_blocks = []
        
        # Add blocks for each day
        for day in range(1, 6):  # MON-FRI
            block = TimeBlock(
                day=day,
                start=540 + (day - 1) * 60,  # Staggered start times
                duration=50,
                course=f"CMSC {140 + day}",
                faculty="Professor",
                room="Full Week Room"
            )
            full_week_blocks.append(block)
        
        panel = RoomPanel("Full Week Room", full_week_blocks)
        
        self.assertEqual(len(panel.blocks), 5)
        
        # Verify each day is represented
        days_covered = {block.day for block in panel.blocks}
        self.assertEqual(days_covered, {1, 2, 3, 4, 5})
    
    def test_mixed_regular_and_lab_blocks(self):
        """Test RoomPanel with mixed regular and lab blocks."""
        mixed_blocks = [
            TimeBlock(day=1, start=540, duration=50, course="CMSC 140", faculty="A", room="R"),
            TimeBlock(day=1, start=600, duration=110, course="CMSC 140", faculty="A", room="R", is_lab=True, lab_name="Linux"),
            TimeBlock(day=3, start=540, duration=50, course="CMSC 140", faculty="A", room="R"),
            TimeBlock(day=3, start=600, duration=110, course="CMSC 140", faculty="A", room="R", is_lab=True, lab_name="Mac"),
        ]
        
        panel = RoomPanel("Mixed Room", mixed_blocks)
        
        self.assertEqual(len(panel.blocks), 4)
        
        # Count lab vs regular blocks
        lab_blocks = [b for b in panel.blocks if b.is_lab]
        regular_blocks = [b for b in panel.blocks if not b.is_lab]
        
        self.assertEqual(len(lab_blocks), 2)
        self.assertEqual(len(regular_blocks), 2)
        
        # Verify lab names are preserved
        lab_names = {b.lab_name for b in lab_blocks}
        self.assertEqual(lab_names, {"Linux", "Mac"})


if __name__ == '__main__':
    unittest.main()