"""Real GUI: repeat Move Original of the same RGBA pixel without new frames."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytestmark = pytest.mark.usefixtures('isolate_gui_recovery')
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_move_original_reposition_same_pixel_repeatedly_then_place_frame():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *a, **k: True
    try:
        source = Image.new('RGBA', (128, 128))
        color = (244, 89, 33, 180)
        source.putpixel((5, 5), color)
        window.model.import_part('source', source)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        window.slimer_move_original.setChecked(True)
        animation = window.anim.currentText()
        initial_frames = len(window.model.animations.get(animation, []))
        for x in (5, 7, 9, 11):
            window.slimer_paint(x, 5, False)
            assert window.slimer_create_editable_layer(), window.status.text()
            pending = window._slimer_pending_part
            assert pending is window.model.parts[-1]
            window.x.setValue(2)
            assert pending['x'] == 2
            assert window.slimer_apply_move_to_pose(), window.status.text()
            assert not window.canvas.slimer_transform_mode, 'Apply Move must finish selection'
            assert window.slimer_selection is not None, 'Slimer stays ready for next highlight'
            assert window.slimer_selection.mask.getbbox() is None, 'Apply Move must clear selection'
            assert window.slimer_selection.source.tobytes() == window.model.render().tobytes()
            assert window.model.render().getpixel((x, 5))[3] == 0, 'Source pixel not cleared'
            assert window.model.render().getpixel((x + 2, 5)) == color, 'RGBA changed'
            assert len(window.model.animations.get(animation, [])) == initial_frames
        # New contract: each committed edit remains a separate editable asset.
        assert sum(p['name'].startswith('Slimer Layer ') for p in window.model.parts) == 4
        assert window.slimer_place_frame(), window.status.text()
        assert len(window.model.animations.get(animation, [])) == initial_frames + 1
        assert window.model.render().getpixel((13, 5)) == color
    finally:
        window.close()
