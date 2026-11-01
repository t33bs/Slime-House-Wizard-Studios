"""Scaled nearest-neighbor source pixels can Move Original without damaging Pose 1."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytestmark = pytest.mark.usefixtures('isolate_gui_recovery')
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_scaled_saved_pose_move_original_uses_exact_source_provenance():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *a, **k: True
    try:
        image = Image.new('RGBA', (2, 2))
        color = (200, 75, 20, 255)
        image.putpixel((0, 0), color)
        window.model.import_part('Scaled source', image)
        window.assets.addItem('Scaled source')
        window.model.resize_part(0, 4, 4)
        name = window.anim.currentText()
        window.model.animations[name] = [window.model.snapshot()]
        window.select_timeline_pose(0)
        window.slimer_toggle.setChecked(True)
        window.slimer_move_original.setChecked(True)
        # Fully select all 4 nearest-neighbor cells of one original pixel.
        for x in (0, 1):
            for y in (0, 1):
                window.slimer_paint(x, y, False)
        assert window.slimer_create_editable_layer(), window.status.text()
        window.x.setValue(5)
        assert window.slimer_apply_move_to_pose(), window.status.text()
        assert window.model.render().getpixel((0, 0))[3] == 0
        assert window.model.render().getpixel((5, 0)) == color
        assert window.model.render(window.model.animations[name][0]).getpixel((0, 0)) == color
    finally:
        window.close()
