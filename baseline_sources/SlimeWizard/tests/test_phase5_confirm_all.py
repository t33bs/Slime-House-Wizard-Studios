"""Phase 5 smoke test: multi-tab placement is atomic and keeps pixel colors."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PIL import Image
import pytest
pytest.importorskip("PySide6")
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_confirm_all_combines_two_tabs_as_one_layer():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    source = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
    source.putpixel((5, 5), (255, 0, 0, 255))
    source.putpixel((10, 10), (0, 0, 255, 255))
    window.model.import_part('source', source)
    window.assets.addItem('source')
    window.slimer_toggle.setChecked(True)
    window.slimer_paint(5, 5, False)
    window.slimer_phase_picker.setCurrentText('Middle')
    window.slimer_paint(10, 10, False)
    window.slimer_dx.setValue(2)
    window.slimer_move_original.setChecked(False)
    before = len(window.model.parts)
    window.slimer_confirm_all_placements()
    assert len(window.model.parts) == before + 1
    image = window.model.parts[-1]['image']
    assert image.getpixel((5, 5)) == (255, 0, 0, 255)
    assert image.getpixel((12, 10)) == (0, 0, 255, 255)
    assert window.model.parts[0]['image'].getpixel((10, 10)) == (0, 0, 255, 255)
    # Test cleanup must not open an interactive unsaved-project dialog.
    # Production close/save behavior remains unchanged.
    window.confirm_unsaved_projects = lambda *args, **kwargs: True
    window.close()
