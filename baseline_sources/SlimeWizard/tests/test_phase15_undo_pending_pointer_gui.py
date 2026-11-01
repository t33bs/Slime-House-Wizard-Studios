"""Qt regression: undo must not leave a stale staged Slimer part pointer."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_undo_staged_creation_releases_pending_identity():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *args, **kwargs: True
    try:
        source = Image.new('RGBA', (128, 128))
        source.putpixel((9, 9), (240, 10, 20, 255))
        window.model.import_part('source', source)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        window.slimer_paint(9, 9, False)
        assert window.slimer_create_editable_layer(), window.status.text()
        assert window._slimer_pending_part is not None
        window.undo()
        assert window._slimer_pending_part is None
        assert window._slimer_pending_layer is None
        assert window._slimer_pending_source is None
        assert window._slimer_pending_mask is None
        assert window.slimer_move_original.isEnabled()
        assert len(window.model.parts) == 1
    finally:
        window.close()
