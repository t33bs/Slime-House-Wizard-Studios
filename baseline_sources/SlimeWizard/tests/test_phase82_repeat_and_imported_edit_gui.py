"""Windows PySide6 acceptance: repeat Slimer without extra pose, and edit imported layers."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication, QFileDialog
from friendly_animator import Suite


def _window():
    app = QApplication.instance() or QApplication([])
    w = Suite()
    w.confirm_unsaved_projects = lambda *a, **kw: True
    return app, w


def _assert_ready_to_highlight(w):
    assert w._slimer_pending_part is None
    assert w._slimer_pending_mask is None
    assert w.canvas.asset_controls_enabled is False
    assert w.canvas.slimer_active is True
    assert w.canvas.slimer_transform_mode is False
    assert w.canvas.slimer_bounds is None
    assert w.slimer_selection.mask.getbbox() is None
    assert w.slimer_selection.source.tobytes() == w.model.render().tobytes()


def test_two_real_button_cycles_same_pose_clear_handles_and_preserve_pixels():
    app, w = _window()
    try:
        source = Image.new('RGBA', (128, 128))
        source.putpixel((16, 16), (230, 30, 50, 255))
        source.putpixel((40, 20), (30, 90, 245, 255))
        w.model.import_part('Swordcat', source)
        w.assets.addItem('Swordcat')
        w.assets.setCurrentRow(0)
        initial_frame_count = len(w.model.animations.get(w.anim.currentText(), []))
        w.slimer_toggle.setChecked(True)
        assert w.slimer_move_original.isChecked()
        for source_xy, dest_x in [((16, 16), 25), ((25, 16), 37)]:
            w.slimer_start_stroke()
            w.slimer_paint(*source_xy, False)
            w.slimer_edit_asset.click()
            assert w._slimer_pending_part is not None, w.status.text()
            assert w.canvas.asset_controls_enabled
            assert not w.canvas.slimer_active
            # A real asset-table edit; Apply Move must end edit mode.
            w.x.setValue(dest_x-source_xy[0])
            assert w.slimer_apply_move_to_pose(), w.status.text()
            _assert_ready_to_highlight(w)
            assert w.model.render().getpixel(source_xy)[3] == 0
            assert w.model.render().getpixel((dest_x, source_xy[1])) == (230, 30, 50, 255)
            assert len(w.model.animations.get(w.anim.currentText(), [])) == initial_frame_count
        assert w.model.render().getpixel((40, 20)) == (30, 90, 245, 255)
    finally:
        w.close()


def test_imported_png_uses_same_edit_button_without_duplicate_or_source_erase(monkeypatch, tmp_path):
    app, w = _window()
    try:
        src=Image.new('RGBA', (24, 24))
        src.putpixel((5, 6), (23, 150, 70, 255))
        file=tmp_path/'imported_leg.png';src.save(file)
        monkeypatch.setattr(QFileDialog, 'getOpenFileNames', lambda *a, **kw: ([str(file)], 'PNG'))
        w.slimer_toggle.setChecked(True)
        w.library_import.click()
        assert w.selected == 0
        assert w.canvas.slimer_active
        assert w.slimer_selection.mask.getbbox() is None
        original_count = len(w.model.parts)
        frames = len(w.model.animations.get(w.anim.currentText(), []))
        w.slimer_edit_asset.click()
        assert len(w.model.parts) == original_count, 'Edit Selection must not duplicate imported asset'
        assert w._slimer_pending_part is None, 'No source erase for direct asset repositioning'
        assert w.canvas.asset_controls_enabled and not w.canvas.slimer_active, w.status.text()
        w.x.setValue(10)
        w.y.setValue(7)
        w.angle.setValue(20)
        assert w.model.parts[0]['x'] == 10
        assert w.model.parts[0]['y'] == 7
        assert w.model.angles.get(0) == 20
        assert w.slimer_apply_move_to_pose(), w.status.text()
        _assert_ready_to_highlight(w)
        assert len(w.model.parts) == original_count
        assert len(w.model.animations.get(w.anim.currentText(), [])) == frames
        assert w.model.originals[0].getpixel((5, 6)) == (23, 150, 70, 255)
    finally:
        w.close()


def test_edit_selection_toggles_existing_imported_handles_off_and_returns_to_brush(monkeypatch, tmp_path):
    app, w = _window()
    try:
        src=Image.new('RGBA', (16, 16));src.putpixel((3, 3), (90, 210, 190, 255))
        file=tmp_path/'slime.png';src.save(file)
        monkeypatch.setattr(QFileDialog, 'getOpenFileNames', lambda *a, **kw: ([str(file)], 'PNG'))
        w.slimer_toggle.setChecked(True)
        w.library_import.click()
        w.slimer_edit_asset.click()
        assert w.canvas.asset_controls_enabled
        w.slimer_edit_asset.click()
        _assert_ready_to_highlight(w)
        assert len(w.model.parts) == 1
    finally:
        w.close()


def test_no_highlight_and_blank_asset_still_refuses_to_create_layer():
    app, w = _window()
    try:
        w.model.import_part('Empty', Image.new('RGBA', (128, 128)))
        w.assets.addItem('Empty');w.assets.setCurrentRow(0)
        w.slimer_toggle.setChecked(True)
        assert not w.slimer_create_editable_layer()
        assert w._slimer_pending_part is None
        assert not w.canvas.asset_controls_enabled
    finally:
        w.close()
