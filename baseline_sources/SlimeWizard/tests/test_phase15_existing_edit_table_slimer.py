"""Exercise the existing asset table against real staged Slimer assets (Windows/Qt)."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_existing_table_transforms_each_new_slimer_layer_without_editing_source():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *a, **kw: True
    try:
        source = Image.new('RGBA', (128, 128))
        for x in (8, 18, 28):
            source.putpixel((x, 8), (255, 0, 0, 255))
        window.model.import_part('source', source)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        window.slimer_move_original.setChecked(False)
        created = []
        for number, x in enumerate((8, 18, 28), 1):
            window.slimer_paint(x, 8, False)
            assert window.slimer_create_editable_layer(), window.status.text()
            pending = window._slimer_pending_part
            assert window.model.parts[window.selected] is pending
            window.x.setValue(number * 3)
            window.y.setValue(number * 4)
            window.angle.setValue(number * 10)
            assert pending['x'] == number * 3
            assert pending['y'] == number * 4
            assert window.model.angles[window.selected] == number * 10
            # While Apply Move is pending, the source row is protected.
            # Attempting to select it redirects the table to the staged layer.
            # Do NOT edit the X spinner after this redirect: that would move
            # the staged destination, not the original source (the old test
            # accidentally set every staged layer's X to 9 this way).
            source_part = window.model.parts[0]
            source_geometry = (source_part['x'], source_part['y'])
            source_pixels = source_part['image'].tobytes()
            staged_geometry = (pending['x'], pending['y'])
            window.assets.setCurrentRow(0)
            assert window.assets.currentRow() == len(window.model.parts) - 1
            assert window.model.parts[window.selected] is pending
            assert (source_part['x'], source_part['y']) == source_geometry
            assert source_part['image'].tobytes() == source_pixels
            assert (pending['x'], pending['y']) == staged_geometry
            assert window.slimer_apply_move_to_pose(), window.status.text()
            assert (source_part['x'], source_part['y']) == source_geometry
            assert source_part['image'].tobytes() == source_pixels
            created.append(pending)
        assert len({id(p) for p in created}) == 3
        assert all(any(p is q for q in window.model.parts) for p in created)
        assert [p['x'] for p in created] == [3, 6, 9]
        assert [p['y'] for p in created] == [4, 8, 12]
    finally:
        window.close()
