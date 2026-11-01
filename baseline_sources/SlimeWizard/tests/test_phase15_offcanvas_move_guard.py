"""Rejected off-canvas staged placement must preserve the source and recover."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytestmark = pytest.mark.usefixtures('isolate_gui_recovery')
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_offcanvas_move_does_not_erase_or_create_frame():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *a, **k: True
    try:
        source = Image.new('RGBA', (128, 128))
        color = (240, 50, 30, 160)
        source.putpixel((5, 5), color)
        window.model.import_part('source', source)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        window.slimer_move_original.setChecked(True)
        before = window.model.render().tobytes()
        animation = window.anim.currentText()
        frame_count = len(window.model.animations.get(animation, []))
        window.slimer_paint(5, 5, False)
        assert window.slimer_create_editable_layer(), window.status.text()
        pending = window._slimer_pending_part
        window.x.setValue(127)
        assert pending['x'] == 127
        assert window.slimer_apply_move_to_pose() is False
        assert window.model.render().tobytes() == before
        assert window.model.parts[0]['image'].getpixel((5, 5)) == color
        assert window._slimer_pending_part is pending  # can reposition and retry
        assert len(window.model.animations.get(animation, [])) == frame_count
        window.x.setValue(2)
        assert window.slimer_apply_move_to_pose(), window.status.text()
        assert window.model.render().getpixel((5, 5))[3] == 0
        assert window.model.render().getpixel((7, 5)) == color
        assert len(window.model.animations.get(animation, [])) == frame_count
    finally:
        window.close()
