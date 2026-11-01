"""GUI regression: partially clipped Move Original must not lose source pixels."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_partially_clipped_destination_rejected_then_repositioned():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *args, **kwargs: True
    try:
        source = Image.new('RGBA', (128, 128))
        source.putpixel((10, 10), (240, 40, 20, 255))
        source.putpixel((20, 10), (20, 80, 240, 255))
        window.model.import_part('source', source)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        window.slimer_move_original.setChecked(True)
        window.slimer_paint(10, 10, False)
        window.slimer_paint(20, 10, False)
        assert window.slimer_create_editable_layer(), window.status.text()
        # Shift the first pixel outside while keeping the second visible.
        window.x.setValue(-15)
        assert not window.slimer_apply_move_to_pose()
        assert 'outside the canvas' in window.status.text()
        assert window._slimer_pending_part is window.model.parts[-1]
        assert window.model.parts[0]['image'].getpixel((10, 10))[3] == 255
        window.x.setValue(30)
        assert window.slimer_apply_move_to_pose(), window.status.text()
        assert window.model.render().getpixel((40, 10))[3] == 255
        assert window.model.render().getpixel((50, 10))[3] == 255
    finally:
        window.close()
