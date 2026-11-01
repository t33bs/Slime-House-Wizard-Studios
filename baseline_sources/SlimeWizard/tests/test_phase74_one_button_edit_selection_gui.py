"""Edit Selection should replace both Finish Selecting and Move Selection UI steps."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


@pytest.mark.parametrize('move_original', [True, False])
def test_one_click_creates_selected_draggable_asset_and_apply_restores_brush(move_original):
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *args, **kwargs: True
    try:
        source = Image.new('RGBA', (128, 128))
        source.putpixel((25, 25), (230, 70, 20, 255))
        source.putpixel((40, 40), (50, 120, 200, 255))
        window.model.import_part('source', source)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        assert window.canvas.slimer_active
        assert window.slimer_move_original.isChecked()  # True by default
        assert window.slimer_drag_toggle.isHidden()  # not an extra user step
        window.slimer_move_original.setChecked(move_original)
        window.slimer_paint(25, 25, False)
        initial_assets = window.assets.count()
        initial_poses = len(window.model.animations.get(window.anim.currentText(), []))
        window.slimer_edit_asset.click()  # the ONLY transition to editing
        assert window.assets.count() == initial_assets + 1, window.status.text()
        assert window._slimer_pending_part is window.model.parts[-1]
        # Staging must NEVER delete the source before Apply Move.
        assert window.model.parts[0]['image'].getpixel((25, 25)) == (230, 70, 20, 255)
        assert window._slimer_pending_move_original is move_original
        assert window.selected == len(window.model.parts) - 1
        assert window.assets.currentRow() == window.selected
        assert not window.canvas.slimer_active  # mouse now moves an actual layer
        assert not window.canvas.slimer_transform_mode
        assert not window.slimer_move_original.isEnabled()
        before = window.model.parts[-1]['x']
        window.canvas.moved.emit(7, 0)  # same canvas mouse-drag signal path
        assert window.model.parts[-1]['x'] == before + 7
        assert window.slimer_apply_move_to_pose(), window.status.text()
        assert window.canvas.slimer_active  # ready to highlight another region
        assert window.slimer_move_original.isEnabled()
        assert window.model.render().getpixel((32, 25)) == (230, 70, 20, 255)
        # Only Apply Move may clear the original when the checkbox was on.
        assert (window.model.parts[0]['image'].getpixel((25, 25))[3] == 0) == move_original
        assert (window.model.render().getpixel((25, 25))[3] == 0) == move_original
        assert window.model.render().getpixel((40, 40)) == (50, 120, 200, 255)
        assert len(window.model.animations.get(window.anim.currentText(), [])) == initial_poses
    finally:
        window.close()


def test_cancel_restores_highlighter_and_original_pixels():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *args, **kwargs: True
    try:
        image = Image.new('RGBA', (128, 128))
        image.putpixel((20, 20), (255, 10, 90, 255))
        window.model.import_part('source', image)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        window.slimer_paint(20, 20, False)
        window.slimer_edit_asset.click()
        assert window._slimer_pending_part is not None, window.status.text()
        assert not window.canvas.slimer_active
        assert window.slimer_cancel_editable_layer(), window.status.text()
        assert window._slimer_pending_part is None
        assert window.canvas.slimer_active
        assert window.slimer_move_original.isChecked()
        assert window.model.render().getpixel((20, 20)) == (255, 10, 90, 255)
    finally:
        window.close()


def test_failed_edit_keeps_highlight_brush_active():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *args, **kwargs: True
    try:
        window.slimer_toggle.setChecked(True)
        window.slimer_edit_asset.click()  # no highlight
        assert window._slimer_pending_part is None
        assert window.canvas.slimer_active
    finally:
        window.close()
