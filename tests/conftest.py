"""Global pytest configuration for GUI tests.

Ensures a QApplication exists before any QWidget is constructed, and
configures Qt to use an offscreen platform in headless CI environments.
"""
from __future__ import annotations

import os
import sys
import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication


@pytest.fixture(scope="session", autouse=True)
def _qt_app_autouse() -> QCoreApplication:
    # Run Qt headless on CI (and safe locally)
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture(autouse=True)
def _qt_messagebox_noop(monkeypatch: pytest.MonkeyPatch):
    """Make QMessageBox calls non-blocking/no-op during tests.

    In headless/offscreen environments, showing native dialogs can crash or hang.
    This fixture ensures information/warning/critical don't create UI and
    question returns a sensible default. Individual tests can still patch these
    methods to assert calls or change return values.
    """
    try:
        from PyQt5.QtWidgets import QMessageBox

        # Return a valid standard button value without showing any UI
        monkeypatch.setattr(QMessageBox, "information", lambda *args, **kwargs: QMessageBox.Ok)
        monkeypatch.setattr(QMessageBox, "warning", lambda *args, **kwargs: QMessageBox.Ok)
        monkeypatch.setattr(QMessageBox, "critical", lambda *args, **kwargs: QMessageBox.Ok)
        # Default to Yes to proceed in flows; tests can override to No as needed
        monkeypatch.setattr(QMessageBox, "question", lambda *args, **kwargs: QMessageBox.Yes)
    except Exception:
        # If PyQt5 isn't available for some reason, don't fail fixture setup
        pass
