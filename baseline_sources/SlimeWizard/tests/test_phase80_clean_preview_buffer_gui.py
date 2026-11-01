"""Phase 80: editor overlays may not contaminate clean preview buffers.

Run under Windows PySide6 and the app's established environment.
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite, pixmap


def _window():
    app = QApplication.instance() or QApplication([])
    w = Suite()
    w.confirm_unsaved_projects = lambda *args, **kwargs: True
    w.resize(1450, 950)
    w.show()
    app.processEvents()
    image = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
    for y in range(45, 60):
        for x in range(40, 48):
            image.putpixel((x, y), (240, 80, 35, 255))
    w.model.import_part('Leg', image)
    w.assets.addItem('Leg')
    w.assets.setCurrentRow(0)
    w.slimer_toggle.setChecked(True)
    for x, y in ((42, 50), (42, 51), (43, 52)):
        w.slimer_paint(x, y, False)
    app.processEvents()
    return app, w


def _clean_preview_matches_model(w):
    # Compare *every* preview pixel, not original canvas coordinates against
    # scaled preview coordinates. The app uses nearest-neighbor scaling to 132.
    expected = pixmap(w.model.render(), 132).toImage()
    actual = w.slimer_preview_label.pixmap().toImage()
    assert not actual.isNull()
    assert expected.size() == actual.size()
    for y in range(expected.height()):
        for x in range(expected.width()):
            assert actual.pixelColor(x, y) == expected.pixelColor(x, y), (x, y)


def test_selection_green_tint_is_canvas_only_and_not_in_slimer_preview():
    app, w = _window()
    try:
        assert w.slimer_selection.mask.getbbox() is not None
        # Exercise selection recolor at least twice: refresh must be repeatable.
        w.refresh()
        app.processEvents()
        _clean_preview_matches_model(w)
        w.refresh()
        app.processEvents()
        _clean_preview_matches_model(w)
    finally:
        w.close()


def test_joint_dot_editor_guide_does_not_contaminate_slimer_preview():
    app, w = _window()
    try:
        w.model.anchors[0] = [42, 51]
        w.refresh()
        app.processEvents()
        _clean_preview_matches_model(w)
    finally:
        w.close()
