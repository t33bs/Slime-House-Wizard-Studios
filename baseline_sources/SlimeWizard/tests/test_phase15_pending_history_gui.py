"""Real Qt regression: Undo of staged Edit Selection returns to intact source."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_undo_staged_layer_does_not_consume_old_brush_history():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *args, **kwargs: True
    try:
        image = Image.new('RGBA', (128, 128))
        image.putpixel((9, 9), (250, 20, 30, 255))
        window.model.import_part('source', image)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        # The UI calls stroke-start before painting; direct slimer_paint()
        # deliberately does not create a separate history entry.
        window.slimer_start_stroke()
        window.slimer_paint(9, 9, False)
        assert window.slimer_selection_undo
        assert window.slimer_create_editable_layer(), window.status.text()
        assert window._slimer_pending_part is not None
        assert window.slimer_selection_undo  # Brush history must not swallow model Undo
        window.undo()
        assert window._slimer_pending_part is None
        assert len(window.model.parts) == 1
        assert window.model.render().getpixel((9, 9)) == (250, 20, 30, 255)
    finally:
        window.close()
