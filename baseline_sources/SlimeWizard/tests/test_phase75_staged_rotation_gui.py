"""Regression: Edit Selection immediately permits rotating the new layer in degrees."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def _artwork():
    image = Image.new('RGBA', (128, 128))
    # Asymmetric 3-pixel shape: rotation is observably different from moving.
    image.putpixel((40, 50), (255, 0, 0, 255))
    image.putpixel((40, 51), (0, 255, 0, 255))
    image.putpixel((41, 51), (0, 0, 255, 255))
    image.putpixel((80, 80), (230, 210, 20, 255))  # unrelated artwork
    return image


@pytest.mark.parametrize('move_original', [True, False])
def test_staged_layer_rotates_around_selected_art_and_applies_safely(move_original):
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *args, **kwargs: True
    try:
        source = _artwork()
        window.model.import_part('source', source)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        window.slimer_move_original.setChecked(move_original)
        for x, y in ((40, 50), (40, 51), (41, 51)):
            window.slimer_paint(x, y, False)
        poses_before = len(window.model.animations.get(window.anim.currentText(), []))
        window.slimer_edit_asset.click()
        pending = window._slimer_pending_part
        assert pending is not None, window.status.text()
        index = window.model.parts.index(pending)
        assert window.model.anchors[index] == [41, 51]
        # A full-canvas layer's rotation handle must be by the selected art.
        pivot, handle, bounds = window.canvas._selected_rotation_geometry(index)
        assert pivot == (41, 51)
        assert bounds == (40, 50, 42, 52)
        assert abs(handle[0]-41) <= 2
        assert 10 <= handle[1] < 51
        assert window.model.parts[0]['image'].tobytes() == source.tobytes()
        # Existing Slimer degree field rotates the staged layer, not its preview.
        window.slimer_turn.setValue(90)
        assert window.model.angles[index] == 90
        assert window.angle.value() == 90
        destination_at_90 = window.model.render_part(index, window.model.resolved_pose()[index])
        assert destination_at_90.getpixel((40, 50))[3] == 0
        assert destination_at_90.getpixel((41, 50)) == (0, 0, 255, 255)
        assert window.model.parts[0]['image'].tobytes() == source.tobytes()
        # The normal Asset Library control and canvas rotation signal stay in sync.
        window.angle.setValue(180)
        assert window.model.angles[index] == 180
        assert window.slimer_turn.value() == 180
        window.canvas.angle_chosen.emit(90)
        assert window.model.angles[index] == 90
        # Move the rotated layer to avoid source/destination overlap.
        window.canvas.moved.emit(10, 5)
        assert window.slimer_apply_move_to_pose(), window.status.text()
        assert window.model.render().getpixel((80, 80)) == (230, 210, 20, 255)
        assert (window.model.parts[0]['image'].getpixel((40, 50))[3] == 0) == move_original
        assert len(window.model.animations.get(window.anim.currentText(), [])) == poses_before
        assert window.canvas.slimer_active
    finally:
        window.close()


def test_cancel_rotated_layer_keeps_original_intact():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *args, **kwargs: True
    try:
        source = _artwork()
        window.model.import_part('source', source)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        window.slimer_paint(40, 50, False)
        window.slimer_edit_asset.click()
        window.slimer_turn.setValue(45)
        assert window.slimer_cancel_editable_layer(), window.status.text()
        assert window.model.parts[0]['image'].tobytes() == source.tobytes()
        assert window.canvas.slimer_active
    finally:
        window.close()


def test_blue_rotation_handle_is_clickable_after_edit_selection():
    """Exercise actual canvas mouse events, not only the angle signal wiring."""
    from PySide6.QtCore import Qt, QPoint
    from PySide6.QtTest import QTest
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *args, **kwargs: True
    try:
        window.resize(1400, 850)
        window.show()
        app.processEvents()
        window.model.import_part('source', _artwork())
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        for x, y in ((40, 50), (40, 51), (41, 51)):
            window.slimer_paint(x, y, False)
        window.slimer_edit_asset.click()
        index = window.selected
        pivot, _, _ = window.canvas._selected_rotation_geometry(index)
        scale, ox, oy = window.canvas._geometry()

        def point(x, y):
            return QPoint(round(ox+x*scale), round(oy+y*scale))

        # Current UI exposes one chosen X/Y/R/S handle, not all four at once.
        # Choose R and click its actual visible screen position (the old
        # geometric handle position is not always the clickable one).
        window.canvas.set_canvas_handle_mode('rotate')
        actual = window.canvas._asset_handle_screen('rotate')
        assert actual is not None
        start = QPoint(round(actual[0]), round(actual[1]))
        assert window.canvas._asset_transform_hit(start) == 'rotate'
        finish = point(pivot[0] + 14, pivot[1])
        QTest.mousePress(window.canvas, Qt.MouseButton.LeftButton, pos=start)
        QTest.mouseMove(window.canvas, pos=finish)
        QTest.mouseRelease(window.canvas, Qt.MouseButton.LeftButton, pos=finish)
        # A Qt mouse event is rounded to an integer *screen* coordinate. On
        # different Windows DPI/zoom layouts, the inverse canvas mapping may
        # yield 89/90/91 degrees for the same nominal quarter-turn gesture.
        # Still require a real near-90-degree rotation, matching angle widgets,
        # and an intact source instead of weakening the interaction check.
        observed = window.model.angles.get(index)
        assert observed is not None
        assert abs(observed - 90) <= 2, observed
        assert window.slimer_turn.value() == observed
        assert window.model.parts[0]['image'].getpixel((40, 50))[3] == 255
    finally:
        window.close()
