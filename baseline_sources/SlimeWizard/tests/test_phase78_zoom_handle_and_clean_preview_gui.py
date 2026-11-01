"""Phase 78 Windows PySide6 gate: reachable controls and clean Slimer Preview.

Run in the established Windows PySide6 virtual environment. This module is
intentionally skipped in the headless source-check environment without Qt.
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite, pixmap


def _window():
    app = QApplication.instance() or QApplication([])
    w = Suite()
    w.confirm_unsaved_projects = lambda *a, **kw: True
    w.resize(1450, 950)
    w.show()
    app.processEvents()
    pic = Image.new('RGBA', (128, 128))
    for y in range(49, 58):
        for x in range(41, 45):
            pic.putpixel((x, y), (240, 80, 35, 255))
    w.model.import_part('Swordcat leg', pic)
    w.assets.addItem('Swordcat leg')
    w.assets.setCurrentRow(0)
    w.slimer_toggle.setChecked(True)
    for x, y in ((42, 50), (42, 51), (42, 52), (43, 52)):
        w.slimer_paint(x, y, False)
    assert w.slimer_create_editable_layer(), w.status.text()
    w.refresh()
    app.processEvents()
    return app, w


def test_zoomed_selected_layer_handles_are_visible_clickable_and_move_original_waits():
    app, w = _window()
    try:
        c = w.canvas
        staged = w._slimer_pending_part
        assert staged is not None and c.asset_controls_enabled
        assert w.slimer_move_original.isChecked()
        original = w.model.parts[0]['image'].tobytes()
        # Deliberately put the selected leg at the right canvas edge; its
        # natural X/rotation handles would fall outside at this zoom.
        c.zoom = 5.0
        scale, ox, oy = c._geometry()
        c.pan_x += c.width() - 12 - (ox + 42.5 * scale)
        c.pan_y += c.height() / 2 - (oy + 51.5 * scale)
        c.update()
        app.processEvents()
        for mode in ('move_x', 'move_y', 'rotate'):
            c.set_canvas_handle_mode(mode)
            location = c._asset_handle_screen()
            assert location is not None
            x, y = location
            assert 21 <= x <= c.width()-21
            assert 21 <= y <= c.height()-21
            assert c._asset_transform_hit(QPoint(round(x), round(y))) == mode
        c.set_canvas_handle_mode('move_x')
        x, y = map(round, c._asset_handle_screen())
        old_x, old_y = staged['x'], staged['y']
        QTest.mousePress(c, Qt.MouseButton.LeftButton, pos=QPoint(x, y))
        QTest.mouseMove(c, pos=QPoint(x - round(3 * scale), y + round(1 * scale)))
        QTest.mouseRelease(c, Qt.MouseButton.LeftButton,
                           pos=QPoint(x - round(3 * scale), y + round(1 * scale)))
        app.processEvents()
        assert staged['x'] == old_x - 3
        assert staged['y'] == old_y
        # The provisional move must never erase source pixels before Apply.
        assert w.model.parts[0]['image'].tobytes() == original
        assert w._slimer_pending_part is staged
        # At the same high zoom the R handle must work, not just appear.
        c.set_canvas_handle_mode('rotate')
        rx, ry = map(round, c._asset_handle_screen())
        scale, ox, oy = c._geometry()
        pivot, _, _ = c._selected_rotation_geometry(w.selected)
        destination = QPoint(round(ox + (pivot[0] - 14) * scale),
                             round(oy + pivot[1] * scale))
        assert 0 < destination.x() < c.width()
        assert 0 < destination.y() < c.height()
        QTest.mousePress(c, Qt.MouseButton.LeftButton, pos=QPoint(rx, ry))
        QTest.mouseMove(c, pos=destination)
        QTest.mouseRelease(c, Qt.MouseButton.LeftButton, pos=destination)
        app.processEvents()
        assert w.model.angles[w.selected] != 0
        assert w.model.parts[0]['image'].tobytes() == original
    finally:
        w.close()


def test_clean_slimer_preview_matches_live_render_without_canvas_tool_overlays():
    app, w = _window()
    try:
        w.canvas.set_canvas_handle_mode('rotate')
        w.refresh()
        app.processEvents()
        expected = pixmap(w.model.render(), 132).toImage()
        actual = w.slimer_preview_label.pixmap().toImage()
        assert not actual.isNull()
        assert expected.size() == actual.size()
        for sample in ((0,0),(42,50),(43,52),(80,80)):
            assert actual.pixelColor(*sample) == expected.pixelColor(*sample)
        assert w.canvas.asset_controls_enabled
        assert w._slimer_pending_part is not None
    finally:
        w.close()
