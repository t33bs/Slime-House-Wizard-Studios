"""Qt regression for redo of provisional Slimer layer."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_undo_redo_restages_layer_instead_of_ordinary_asset():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *args, **kwargs: True
    try:
        image = Image.new('RGBA', (128, 128))
        image.putpixel((9, 9), (250, 20, 30, 255))
        window.model.import_part('source', image)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        window.slimer_paint(9, 9, False)
        assert window.slimer_create_editable_layer(), window.status.text()
        window.undo()
        assert window._slimer_pending_part is None
        window.redo()
        assert window._slimer_pending_part is window.model.parts[-1]
        assert window._slimer_pending_layer == len(window.model.parts) - 1
        assert not window.slimer_move_original.isEnabled()
        assert window.slimer_cancel_editable_layer()
        assert len(window.model.parts) == 1
    finally:
        window.close()
