"""Move Original then Copy Pixels creates independent editable layers, no frames."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytestmark = pytest.mark.usefixtures('isolate_gui_recovery')
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_move_original_then_copy_without_adding_frames():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *args, **kwargs: True
    try:
        source = Image.new('RGBA', (128, 128))
        source.putpixel((5, 5), (255, 0, 0, 255))
        source.putpixel((10, 10), (0, 0, 255, 255))
        window.model.import_part('source', source)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        animation = window.anim.currentText()
        initial_frames = len(window.model.animations.get(animation, []))

        window.slimer_move_original.setChecked(True)
        window.slimer_paint(5, 5, False)
        assert window.slimer_create_editable_layer(), window.status.text()
        window.x.setValue(2)
        assert window.slimer_apply_move_to_pose(), window.status.text()
        assert window.model.render().getpixel((5, 5))[3] == 0
        assert window.model.render().getpixel((7, 5)) == (255, 0, 0, 255)

        window.slimer_move_original.setChecked(False)
        window.slimer_paint(10, 10, False)
        assert window.slimer_create_editable_layer(), window.status.text()
        window.x.setValue(3)
        assert window.slimer_apply_move_to_pose(), window.status.text()
        rendered = window.model.render()
        assert rendered.getpixel((10, 10)) == (0, 0, 255, 255)
        assert rendered.getpixel((13, 10)) == (0, 0, 255, 255)
        assert rendered.getpixel((7, 5)) == (255, 0, 0, 255)
        assert len(window.model.animations.get(animation, [])) == initial_frames
        assert sum(p['name'].startswith('Slimer Layer ') for p in window.model.parts) == 2
    finally:
        window.close()
