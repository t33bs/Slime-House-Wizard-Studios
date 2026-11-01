"""Windows PySide6 verification of Phase 103 skin without tool changes."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QComboBox, QCheckBox
from friendly_animator import Suite

pytestmark = pytest.mark.usefixtures('isolate_gui_recovery')


def test_right_dock_is_styled_with_exactly_one_buddy_switch():
    app = QApplication.instance() or QApplication([])
    w = Suite()
    w.confirm_unsaved_projects = lambda *a, **k: True
    try:
        original_fingerprint = w.model.content_fingerprint()
        for name in ('pixelBuddyWorkspaceHeading', 'pixelBuddyMascot', 'pixelBuddySpeechBubble',
                     'pixelBuddyProductionHeading', 'pixelBuddyProductionExplainer',
                     'buddyProductionStatus', 'pixelBuddyHandoffLabel',
                     'pixelAnimationPreviewHeading', 'pixelSlimerPreviewHeading',
                     'pixelCreaturePreviewHeading', 'pixelSlimerCleanPreview',
                     'pixelFramePreviewImage', 'pixelPreviewSpeedHeading'):
            assert w.findChild(QLabel, name) is not None, name
        assert w.findChild(QLabel, 'pixelBuddyMascot') is w.buddy_mascot
        assert w.findChild(QLabel, 'pixelBuddySpeechBubble') is w.buddy_bubble
        assert w.findChild(QLabel, 'pixelFramePreviewImage') is w.preview
        assert w.findChild(QLabel, 'pixelSlimerCleanPreview') is w.slimer_preview_label
        for name in ('pixelPreviewZoomOut', 'pixelPreviewZoomIn', 'pixelPreviewZoomFit',
                     'animationPreviewCollapseButton', 'pixelPreviewPlayButton'):
            assert w.findChild(QPushButton, name) is not None, name
        assert w.findChild(QComboBox, 'pixelPreviewSpeedSelect') is w.speed
        assert w.findChild(QCheckBox, 'pixelPreviewLoopCheck') is w.loop
        assert len(w.findChildren(QCheckBox, 'topSlimeBuddyToggle')) == 1
        assert w.buddy_production_status.text().startswith('● Production engine not connected')
        assert w.model.content_fingerprint() == original_fingerprint
        assert w.preview is not None and w.slimer_toggle.isEnabled()
    finally:
        w.close()


def test_collapse_does_not_touch_artwork_or_replace_preview_controls():
    app = QApplication.instance() or QApplication([])
    w = Suite()
    w.confirm_unsaved_projects = lambda *a, **k: True
    previous = w.settings.value('animation_preview_collapsed', False, type=bool)
    try:
        w.set_animation_preview_collapsed(False, announce=False)
        original_fingerprint = w.model.content_fingerprint()
        original_ids = (id(w.preview), id(w.play), id(w.speed), id(w.loop), id(w.buddy_mascot))
        w.animation_preview_toggle.click()
        assert w.animation_preview_body.isHidden()
        w.animation_preview_toggle.click()
        assert not w.animation_preview_body.isHidden()
        assert original_ids == (id(w.preview), id(w.play), id(w.speed), id(w.loop), id(w.buddy_mascot))
        assert w.model.content_fingerprint() == original_fingerprint
    finally:
        w.set_animation_preview_collapsed(previous, announce=False)
        w.close()
