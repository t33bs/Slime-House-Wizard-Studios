"""Phase 84: the yellow rotation pivot is NOT a permanent canvas knob.

PySide6 Windows gate for Slimer's automatically created joint/pivot marker.
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest

# Test Suite windows must never trigger hidden recovery dialogs or touch actual backups.
pytestmark = pytest.mark.usefixtures("isolate_gui_recovery")
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def _window():
    app = QApplication.instance() or QApplication([])
    w = Suite()
    w.confirm_unsaved_projects = lambda *a, **k: True
    return app, w


def _canvas_pixels(w):
    return w.canvas._art.toImage()


def _model_pixels(w):
    from PySide6.QtGui import QImage
    rgba = w.model.render().convert('RGBA')
    data = rgba.tobytes('raw', 'RGBA')
    return QImage(data, rgba.width, rgba.height, rgba.width * 4,
                  QImage.Format.Format_RGBA8888).copy()


def test_stored_anchor_is_hidden_until_place_joint_mode_is_on():
    app, w = _window()
    try:
        im = Image.new('RGBA', (128, 128))
        for y in range(26, 40):
            for x in range(30, 47):
                im.putpixel((x, y), (110, 90, 140, 255))
        w.model.import_part('Leg', im)
        w.assets.addItem('Leg')
        w.assets.setCurrentRow(0)
        w.model.set_anchor(0, 38, 33)
        w.refresh()
        app.processEvents()
        # Anchor remains functional model state, but its yellow marker is off.
        assert w.model.anchors[0] == [38, 33]
        assert _canvas_pixels(w).pixelColor(38, 33) == _model_pixels(w).pixelColor(38, 33)
        w.anchor_button.setChecked(True)
        app.processEvents()
        assert _canvas_pixels(w).pixelColor(38, 33) != _model_pixels(w).pixelColor(38, 33)
        w.anchor_button.setChecked(False)
        app.processEvents()
        assert _canvas_pixels(w).pixelColor(38, 33) == _model_pixels(w).pixelColor(38, 33)
        assert w.model.anchors[0] == [38, 33]
    finally:
        w.close()


def test_slimer_auto_rotation_pivot_does_not_leave_yellow_guide_after_apply():
    app, w = _window()
    try:
        im = Image.new('RGBA', (128,128))
        for y in range(32, 42):
            for x in range(20, 32):
                im.putpixel((x,y), (120,60,180,255))
        w.model.import_part('Swordcat', im)
        w.assets.addItem('Swordcat')
        w.assets.setCurrentRow(0)
        w.slimer_toggle.setChecked(True)
        assert w.slimer_move_original.isChecked()
        w.slimer_paint(25, 35, False)
        assert w.slimer_create_editable_layer(), w.status.text()
        pending = w._slimer_pending_part
        assert pending is not None
        staged_index = w.model.parts.index(pending)
        assert staged_index in w.model.anchors
        pending['x'] = 5
        assert w.slimer_apply_move_to_pose(), w.status.text()
        app.processEvents()
        assert not w.canvas.anchor_mode
        assert w.canvas.asset_controls_enabled is False
        assert w._slimer_pending_part is None
        assert staged_index in w.model.anchors, 'The rotation pivot remains stored.'
        # No yellow guide should be painted after Apply Move, even though
        # the new layer still has an anchor and the Slimer tool stays active.
        assert _canvas_pixels(w).pixelColor(28, 35) == _model_pixels(w).pixelColor(28, 35)
        # Check all pixels so the test cannot miss a misplaced yellow guide.
        canvas = _canvas_pixels(w); model = _model_pixels(w)
        for yy in range(128):
            for xx in range(128):
                assert canvas.pixelColor(xx, yy) == model.pixelColor(xx, yy), (xx, yy)
    finally:
        w.close()
