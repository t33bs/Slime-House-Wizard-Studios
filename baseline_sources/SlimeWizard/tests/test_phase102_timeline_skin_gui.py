"""Windows Qt test: restyled timeline retains every existing control and model."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QSpinBox, QToolButton, QListWidget
from friendly_animator import Suite

pytestmark = pytest.mark.usefixtures('isolate_gui_recovery')


def test_timeline_is_styled_and_preserves_frame_editing_connections():
    app = QApplication.instance() or QApplication([])
    w = Suite()
    w.confirm_unsaved_projects = lambda *a, **k: True
    try:
        before = w.model.content_fingerprint()
        assert w.findChild(QListWidget, 'pixelPoseTimeline') is w.timeline
        assert w.findChild(QSpinBox, 'pixelTimelineDuration') is w.duration
        assert w.findChild(QLabel, 'pixelTimelineHeading') is not None
        assert w.findChild(QLabel, 'pixelTimelineTimingCaption') is not None
        assert w.findChild(QToolButton, 'pixelTimelineImportPose') is w.pose_png_import_button
        for name in ('pixelTimelineSavePose', 'pixelTimelineRestorePose',
                     'pixelTimelineDuplicatePose', 'pixelTimelinePreviousPose',
                     'pixelTimelineNextPose', 'pixelTimelineInsertPose',
                     'pixelTimelineCopyPose', 'pixelTimelineRemovePose',
                     'pixelTimelineShiftLeft', 'pixelTimelineShiftRight'):
            button = w.findChild(QPushButton, name)
            assert button is not None, name
            assert button.isEnabled(), name
        assert w.timeline.dragEnabled()
        assert w.timeline.acceptDrops()
        assert w.model.content_fingerprint() == before
    finally:
        w.close()
