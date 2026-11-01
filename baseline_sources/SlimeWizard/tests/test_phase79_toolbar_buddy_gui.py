"""Phase 79 Windows PySide6 GUI gate: larger canvas and top Slime Buddy switch."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
pytest.importorskip('PySide6')
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication, QComboBox, QPushButton, QCheckBox
from friendly_animator import Suite


def _open():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *a, **kw: True
    window.resize(1500, 980)
    window.show()
    app.processEvents()
    return app, window


def test_no_redundant_station_menu_or_readiness_row_and_buddy_near_top():
    app, window = _open()
    try:
        assert not hasattr(window, 'buddy_station')
        assert not hasattr(window, 'check_button')
        assert not any(button.text() == '✓ Check animation readiness'
                       for button in window.findChildren(QPushButton))
        assert not any(combo.toolTip().startswith('Choose the station')
                       for combo in window.findChildren(QComboBox))
        assert window.buddy_toggle.objectName() == 'topSlimeBuddyToggle'
        assert window.buddy_toggle.parent() is window.mode.parent()
        buddy_y = window.buddy_toggle.mapTo(window, QPoint(0, 0)).y()
        canvas_y = window.canvas.mapTo(window, QPoint(0, 0)).y()
        assert 0 < buddy_y < canvas_y
        # The canvas follows its descriptive heading, with no station/readiness
        # widgets occupying vertical layout rows in between.
        mid_layout = window.canvas.parentWidget().layout()
        assert mid_layout.indexOf(window.canvas) == 1
        assert window.canvas.height() >= 380
        assert any(button.text() == 'Import PNG assets'
                   for button in window.findChildren(QPushButton))
    finally:
        window.close()


def test_single_top_toggle_persists_and_controls_buddy_guidance():
    app, window = _open()
    initial = window.buddy_toggle.isChecked()
    try:
        window.buddy_toggle.setChecked(False)
        app.processEvents()
        assert not hasattr(window, 'buddy_dock_toggle')
        assert len(window.findChildren(QCheckBox, 'topSlimeBuddyToggle')) == 1
        assert window.buddy_mascot.isHidden()
        assert window.buddy_bubble.isHidden()
        assert window.settings.value('slime_buddy_enabled', type=bool) is False
        window.buddy_toggle.setChecked(True)
        app.processEvents()
        assert window.buddy_toggle.isChecked()
        assert not window.buddy_bubble.isHidden()
        assert window.settings.value('slime_buddy_enabled', type=bool) is True
        # The workflow stays available regardless of Buddy's state.
        assert window.slimer_toggle.isEnabled()
        assert window.canvas.isEnabled()
    finally:
        window.buddy_toggle.setChecked(initial)
        window.close()
