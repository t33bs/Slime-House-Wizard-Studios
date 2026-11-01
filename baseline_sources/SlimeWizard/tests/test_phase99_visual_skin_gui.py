"""Windows Qt acceptance for Phase 99's visual-only shell and existing buttons."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
pytestmark = pytest.mark.usefixtures('isolate_gui_recovery')
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication, QLabel, QPushButton
from friendly_animator import Suite


def _open():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *a, **k: True
    window.resize(1500, 960)
    window.show()
    app.processEvents()
    return app, window


def test_pixel_shell_is_visible_and_keeps_existing_editing_controls():
    app, w = _open()
    try:
        assert w.findChild(QLabel, 'pixelAppTitle').text() == 'Slime Wizard'
        assert w.findChild(QLabel, 'pixelAppSubtitle').isVisible()
        assert 'QPushButton, QToolButton' in w.styleSheet()
        assert w.slimer_toggle.isEnabled()
        assert w.slimer_apply_move.isEnabled()
        assert w.cleaner_toggle.isEnabled()
        assert w.slimer_place_frame_button.isEnabled()
        assert w.slimer_place_frame_button.property('uiRole') == 'primary'
        assert w.slimer_apply_move.property('uiRole') == 'success'
        assert w.timeline.objectName() == 'pixelPoseTimeline'
        assert w.buddy_workspace_panel.isVisible()
        assert w.animation_preview_section.isVisible()
    finally:
        w.close()


def test_button_skin_and_preview_collapse_do_not_change_sprite_data():
    app, w = _open()
    old = w.settings.value('animation_preview_collapsed', False, type=bool)
    try:
        fingerprint = w.model.content_fingerprint()
        assert w.findChildren(QPushButton)
        w.set_animation_preview_collapsed(True, announce=False)
        app.processEvents()
        assert w.animation_preview_body.isHidden()
        assert w.model.content_fingerprint() == fingerprint
        w.set_animation_preview_collapsed(False, announce=False)
        app.processEvents()
        assert w.animation_preview_body.isVisible()
        assert w.model.content_fingerprint() == fingerprint
    finally:
        w.set_animation_preview_collapsed(old, announce=False)
        w.close()
