"""Real Qt signal integration for staged Slimer layers (runs with PySide6)."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_copy_pixels_two_rounds_with_live_spinbox_and_no_manual_slot_call():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *a, **kw: True
    try:
        source = Image.new('RGBA', (128, 128))
        source.putpixel((10, 10), (20, 220, 70, 255))
        window.model.import_part('source', source)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        window.slimer_move_original.setChecked(False)
        original_pose_count = len(window.model.animations.get(window.anim.currentText(), []))
        for destination in (30, 50):
            window.slimer_paint(10, 10, False)
            assert window.slimer_create_editable_layer(), window.status.text()
            part = window._slimer_pending_part
            assert part is window.model.parts[-1]
            assert window.model.parts[window.selected] is part
            # Test actual QSpinBox.valueChanged signal, not a direct slot call.
            window.x.setValue(destination - 10)
            assert part['x'] == destination - 10
            assert window.slimer_apply_move_to_pose(), window.status.text()
            assert window.model.render().getpixel((destination, 10)) == (20, 220, 70, 255)
            assert window._slimer_pending_part is None
        assert window.model.render().getpixel((10, 10)) == (20, 220, 70, 255)
        assert len(window.model.parts) == 3
        assert len(window.model.animations.get(window.anim.currentText(), [])) == original_pose_count
    finally:
        window.close()
