"""Windows GUI cue: Edit Selection lights up exactly when handles are active.

The highlight is presentation only; it must not accidentally create assets,
erase source pixels, or add frames. Opt out of real recovery I/O.
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image

pytestmark = pytest.mark.usefixtures('isolate_gui_recovery')
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def make_window():
    app = QApplication.instance() or QApplication([])
    w = Suite()
    w.confirm_unsaved_projects = lambda *a, **k: True
    w.show()
    app.processEvents()
    return w


def is_lit(w):
    return (w.slimer_edit_asset.property('editingActive') is True
            and '#c8ff87' in w.slimer_edit_asset.styleSheet()
            and w.canvas.asset_controls_enabled)


def is_unlit(w):
    return (w.slimer_edit_asset.property('editingActive') is False
            and not w.slimer_edit_asset.styleSheet()
            and not w.canvas.asset_controls_enabled)


def test_staged_edit_selection_lights_and_clears_after_apply_move():
    w = make_window()
    try:
        assert is_unlit(w)
        art = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
        art.putpixel((28, 31), (240, 90, 20, 255))
        w.model.import_part('Swordcat', art)
        w.assets.addItem('Swordcat')
        w.assets.setCurrentRow(0)
        w.slimer_toggle.setChecked(True)
        w.slimer_paint(28, 31, False)
        assert is_unlit(w), 'Painting a highlight is not yet edit mode'
        w.slimer_edit_asset.click()
        assert w._slimer_pending_part is not None
        assert is_lit(w)
        assert 'Hide Handles' in w.slimer_edit_asset.text()
        staged = w._slimer_pending_part
        # Toggling handles does not cancel the staged layer.
        w.slimer_edit_asset.click()
        assert is_unlit(w)
        assert w._slimer_pending_part is staged
        w.slimer_edit_asset.click()
        assert is_lit(w)
        assert w._slimer_pending_part is staged
        staged['x'] = 3
        assert w.slimer_apply_move_to_pose(), w.status.text()
        assert is_unlit(w)
        assert w.model.render().getpixel((28, 31))[3] == 0
        assert w.model.render().getpixel((31, 31)) == (240, 90, 20, 255)
    finally:
        w.close()


def test_existing_asset_edit_mode_lights_and_clears_without_new_part():
    w = make_window()
    try:
        source = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
        source.putpixel((40, 45), (90, 130, 220, 255))
        w.model.import_part('Existing art', source)
        w.assets.addItem('Existing art')
        w.assets.setCurrentRow(0)
        w.slimer_toggle.setChecked(True)
        original_count = len(w.model.parts)
        w.slimer_edit_asset.click()
        assert is_lit(w)
        assert len(w.model.parts) == original_count
        w.slimer_edit_asset.click()
        assert is_unlit(w)
        assert len(w.model.parts) == original_count
        w.slimer_edit_asset.click()
        assert is_lit(w)
        assert w.slimer_apply_move_to_pose(), w.status.text()
        assert is_unlit(w)
        assert len(w.model.parts) == original_count
    finally:
        w.close()


def test_rejected_edit_does_not_light_button():
    w = make_window()
    try:
        w.slimer_toggle.setChecked(True)
        assert is_unlit(w)
        w.slimer_edit_asset.click()
        assert is_unlit(w)
        assert w._slimer_pending_part is None
    finally:
        w.close()
