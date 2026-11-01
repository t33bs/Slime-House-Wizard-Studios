"""Phase 97 Windows gate: Buddy's own production dock and collapsible previews.

Only layout changes are allowed; pose snapshots, playback objects and existing
Slimer tools must remain intact. The real AI engine is intentionally NOT wired.
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
pytestmark = pytest.mark.usefixtures('isolate_gui_recovery')
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def _open():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *a, **k: True
    window.resize(1500, 950)
    window.show()
    app.processEvents()
    return app, window


def test_collapse_and_expand_only_preview_without_changing_editor():
    app, w = _open()
    prior = w.settings.value('animation_preview_collapsed', False, type=bool)
    try:
        w.set_animation_preview_collapsed(False)
        app.processEvents()
        before = w.model.content_fingerprint()
        saved_ids = {name: [id(pose) for pose in poses]
                     for name, poses in w.model.animations.items()}
        assert w.buddy_workspace_panel.isVisible()
        assert w.animation_preview_body.isVisible()
        assert w.buddy_production_status.text().startswith('● Production engine not connected')
        assert w.buddy_mascot.pixmap() is not None
        assert not w.buddy_mascot.pixmap().isNull()
        w.animation_preview_toggle.click()
        app.processEvents()
        assert w._animation_preview_collapsed
        assert w.animation_preview_body.isHidden()
        assert w.animation_preview_section.isVisible()
        assert w.buddy_workspace_panel.isVisible()
        assert w.preview is not None and w.slimer_preview_label is not None
        assert w.play is not None and w.speed is not None and w.loop is not None
        assert w.slimer_toggle.isEnabled()
        assert w.model.content_fingerprint() == before
        assert {name: [id(pose) for pose in poses]
                for name, poses in w.model.animations.items()} == saved_ids
        w.animation_preview_toggle.click()
        app.processEvents()
        assert not w._animation_preview_collapsed
        assert w.animation_preview_body.isVisible()
        assert w.model.content_fingerprint() == before
    finally:
        w.set_animation_preview_collapsed(prior, announce=False)
        w.close()


def test_preview_collapse_preference_survives_window_reopen():
    app, w = _open()
    prior = w.settings.value('animation_preview_collapsed', False, type=bool)
    try:
        w.set_animation_preview_collapsed(True)
        w.close()
        w2 = Suite()
        w2.confirm_unsaved_projects = lambda *a, **k: True
        w2.show()
        app.processEvents()
        try:
            assert w2._animation_preview_collapsed
            assert w2.animation_preview_body.isHidden()
            assert w2.buddy_workspace_panel.isVisible()
            assert w2.animation_preview_toggle.text().endswith('Expand')
        finally:
            w2.set_animation_preview_collapsed(prior, announce=False)
            w2.close()
    finally:
        w.settings.setValue('animation_preview_collapsed', prior)


def test_buddy_on_off_keeps_human_tools_and_preview_working():
    app, w = _open()
    original = w.buddy_toggle.isChecked()
    try:
        w.buddy_toggle.setChecked(False)
        app.processEvents()
        assert w.buddy_mascot.isHidden()
        assert w.buddy_bubble.isHidden()
        assert w.slimer_toggle.isEnabled()
        assert w.animation_preview_toggle.isEnabled()
        assert w.buddy_production_status.isVisible()
        w.buddy_toggle.setChecked(True)
        app.processEvents()
        assert w.buddy_mascot.isVisible()
        assert w.buddy_bubble.isVisible()
    finally:
        w.buddy_toggle.setChecked(original)
        w.close()
