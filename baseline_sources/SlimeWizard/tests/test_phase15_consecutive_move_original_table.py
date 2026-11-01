"""Windows/Qt regression: repeated Move Original through the existing asset table."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_three_consecutive_move_original_operations_keep_distinct_editable_layers():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *a, **kw: True
    try:
        source = Image.new('RGBA', (128, 128))
        for x in (12, 32, 52):
            source.putpixel((x, 12), (255, 40, 40, 255))
        window.model.import_part('source', source)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        window.slimer_move_original.setChecked(True)
        created = []
        for n, original_x in enumerate((12, 32, 52), 1):
            window.slimer_paint(original_x, 12, False)
            assert window.slimer_create_editable_layer(), window.status.text()
            part = window._slimer_pending_part
            assert window.model.parts[window.selected] is part
            # The existing editing table edits the staged destination, not its source.
            window.x.setValue(n * 2)
            assert part['x'] == n * 2
            assert window.slimer_apply_move_to_pose(), window.status.text()
            assert window._slimer_pending_part is None
            assert window.model.parts[0]['image'].getpixel((original_x, 12))[3] == 0
            created.append(part)
        assert len({id(p) for p in created}) == 3
        assert [p['x'] for p in created] == [2, 4, 6]
        assert all(any(p is candidate for candidate in window.model.parts) for p in created)
    finally:
        window.close()
