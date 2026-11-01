"""Windows PySide6 GUI tests for center visual pass and single Buddy toggle."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication, QCheckBox, QTabBar, QPushButton, QLabel
from friendly_animator import Suite

pytestmark = pytest.mark.usefixtures('isolate_gui_recovery')


def _window():
    app = QApplication.instance() or QApplication([])
    w = Suite()
    w.confirm_unsaved_projects = lambda *a, **k: True
    w.resize(1500, 960)
    w.show()
    app.processEvents()
    return app, w


def test_center_controls_keep_existing_bindings_and_model():
    app, w = _window()
    try:
        fingerprint = w.model.content_fingerprint()
        assert w.canvas.objectName() == 'pixelMainCanvas'
        assert w.findChild(QTabBar, 'pixelWorkspaceTabs') is w.workspace_tabs
        assert w.findChild(QLabel, 'pixelZoomReadout') is w.zoom_label
        assert w.findChild(QPushButton, 'pixelCanvasFitButton') is not None
        assert w.add_workspace.objectName() == 'pixelWorkspaceAddButton'
        assert w.canvas.isEnabled()
        assert w.timeline.isEnabled()
        assert w.model.content_fingerprint() == fingerprint
    finally:
        w.close()


def test_only_one_slime_buddy_switch_and_it_persists():
    app, w = _window()
    original = w.buddy_toggle.isChecked()
    try:
        assert len(w.findChildren(QCheckBox, 'topSlimeBuddyToggle')) == 1
        assert not hasattr(w, 'buddy_dock_toggle')
        before = w.model.content_fingerprint()
        w.buddy_toggle.setChecked(False)
        app.processEvents()
        assert w.buddy_mascot.isHidden() and w.buddy_bubble.isHidden()
        assert w.settings.value('slime_buddy_enabled', type=bool) is False
        assert w.slimer_toggle.isEnabled() and w.cleaner_toggle.isEnabled()
        w.buddy_toggle.setChecked(True)
        app.processEvents()
        assert w.buddy_mascot.isVisible() and w.buddy_bubble.isVisible()
        assert w.settings.value('slime_buddy_enabled', type=bool) is True
        assert w.model.content_fingerprint() == before
    finally:
        w.buddy_toggle.setChecked(original)
        w.close()
