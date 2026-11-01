"""Repeated staged Slimer edits and Undo/Redo preserve final artwork."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytestmark = pytest.mark.usefixtures('isolate_gui_recovery')
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_move_same_pixel_twice_then_undo_and_redo():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *args, **kwargs: True
    try:
        source = Image.new('RGBA', (128, 128))
        color = (231, 72, 44, 255)
        source.putpixel((5, 5), color)
        window.model.import_part('source', source)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        window.slimer_move_original.setChecked(True)
        animation = window.anim.currentText()
        initial_frames = len(window.model.animations.get(animation, []))

        for start_x, end_x in ((5, 7), (7, 9)):
            window.slimer_paint(start_x, 5, False)
            assert window.slimer_create_editable_layer(), window.status.text()
            window.x.setValue(end_x - start_x)
            assert window.slimer_apply_move_to_pose(), window.status.text()
            assert window.slimer_selection.mask.getbbox() is None
            assert window.model.render().getpixel((start_x, 5))[3] == 0
            assert window.model.render().getpixel((end_x, 5)) == color
            assert len(window.model.animations.get(animation, [])) == initial_frames
        assert sum(p['name'].startswith('Slimer Layer ') for p in window.model.parts) == 2
        committed = window.model.render().tobytes()
        window.undo()
        window.redo()
        assert window.model.render().tobytes() == committed
        assert window.model.render().getpixel((9, 5)) == color
        assert window.model.render().getpixel((7, 5))[3] == 0
    finally:
        window.close()
