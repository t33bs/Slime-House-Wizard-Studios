"""Phase 73: user-facing Edit Selection button must stage an editable layer."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite

@pytest.mark.parametrize('move_original', [True, False])
def test_highlight_click_edit_selection_then_apply(move_original):
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *args, **kwargs: True
    try:
        image = Image.new('RGBA', (128, 128))
        image.putpixel((25, 25), (240, 30, 20, 255))
        window.model.import_part('source', image)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        window.slimer_move_original.setChecked(move_original)
        window.slimer_paint(25, 25, False)
        assert window.slimer_selection.mask.getbbox() is not None
        before = window.assets.count()
        window.slimer_edit_asset.click()
        assert window.assets.count() == before + 1, window.status.text()
        assert window._slimer_pending_part is window.model.parts[-1]
        assert not window.slimer_move_original.isEnabled()
        window.x.setValue(window.x.value() + 5)
        assert window.slimer_apply_move_to_pose(), window.status.text()
        assert window._slimer_pending_part is None
        assert window.slimer_move_original.isEnabled()
        rendered = window.model.render()
        assert rendered.getpixel((30, 25))[3] > 0
        assert (rendered.getpixel((25, 25))[3] == 0) == move_original
    finally:
        window.close()
