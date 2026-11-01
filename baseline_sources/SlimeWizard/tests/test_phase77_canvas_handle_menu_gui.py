"""Phase 77: one on-canvas, collapsible X/Y/R handle picker per active layer.

Run using the user's configured Windows PySide6 environment.
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from PIL import Image
from friendly_animator import Suite


def _window():
    app = QApplication.instance() or QApplication([])
    w = Suite()
    w.confirm_unsaved_projects = lambda *a, **kw: True
    w.resize(1400, 900)
    w.show()
    app.processEvents()
    source = Image.new('RGBA', (128,128), (0,0,0,0))
    source.putpixel((40,50), (255,80,20,255))
    w.model.import_part('Swordcat arm', source)
    w.assets.addItem('Swordcat arm')
    w.assets.setCurrentRow(0)
    w.refresh()
    return app, w


def test_collapsible_menu_is_child_of_canvas_and_defaults_to_x():
    app, w = _window()
    try:
        canvas = w.canvas
        assert canvas.handle_panel.parent() is canvas
        assert canvas.handle_panel.isVisible()
        assert not canvas.handle_menu_details.isVisible()
        assert canvas.asset_handle_mode == 'move_x'
        assert canvas.handle_mode_picker.count() == 4
        assert canvas.handle_layer_picker.count() == 1
        assert canvas.handle_layer_picker.currentText() == '1. Swordcat arm'
        assert canvas.handle_panel.x() >= 0
        canvas.handle_menu_button.click()
        app.processEvents()
        assert canvas.handle_menu_details.isVisible()
        assert canvas.handle_panel.x() + canvas.handle_panel.width() <= canvas.width()
        canvas.handle_menu_button.click()
        assert not canvas.handle_menu_details.isVisible()
    finally:
        w.close()


def test_mode_dropdown_exposes_only_selected_handle_and_edit_toggle():
    app, w = _window()
    try:
        c = w.canvas
        w.slimer_edit_asset.click()  # Existing layer: toggles handles on.
        assert c.asset_controls_enabled
        assert not c.slimer_active
        _, handles, _ = c._asset_transform_geometry(w.selected)
        scale, ox, oy = c._geometry()
        class Point:
            def __init__(self, xy):
                self.px, self.py = xy
            def x(self): return self.px
            def y(self): return self.py
        def hit(mode):
            x, y = handles[mode]
            return c._asset_transform_hit(Point((ox + x*scale, oy + y*scale)))
        for mode in ('move_x','move_y','rotate','resize'):
            c.set_canvas_handle_mode(mode)
            assert c.asset_handle_mode == mode
            assert hit(mode) == mode
            for other in ('move_x','move_y','rotate','resize'):
                if other != mode:
                    # Geometry may overlap at extreme zoom; these positions are
                    # distinct for our artwork's full-canvas layer.
                    x, y = handles[mode]
                    u, v = handles[other]
                    if ((x-u)*scale)**2 + ((y-v)*scale)**2 > 13**2:
                        assert hit(other) is None
            assert 'Handles ON: ' + {'move_x':'X','move_y':'Y','rotate':'R','resize':'S'}[mode] in w.active_asset_label.text()
        w.slimer_edit_asset.click()
        assert not c.asset_controls_enabled
        assert hit('rotate') is None
    finally:
        w.close()


def test_on_canvas_layer_picker_stays_in_sync_and_cannot_switch_during_move_original():
    app, w = _window()
    try:
        c = w.canvas
        w.model.import_part('Swordcat sword', Image.new('RGBA',(128,128),(0,0,0,0)))
        w.assets.addItem('Swordcat sword')
        w.refresh()
        c.handle_layer_picker.setCurrentIndex(1)
        assert w.assets.currentRow() == 1 and w.selected == 1
        c.handle_layer_picker.setCurrentIndex(0)
        assert w.selected == 0
        w.slimer_toggle.setChecked(True)
        w.slimer_paint(40,50,False)
        assert w.slimer_create_editable_layer(), w.status.text()
        assert w._slimer_pending_part is not None
        assert not c.handle_layer_picker.isEnabled()
        assert c.handle_layer_picker.currentIndex() == w.selected
        assert w.slimer_move_original.isChecked()
        assert w.model.parts[0]['image'].getpixel((40,50))[3] == 255
        assert w.slimer_cancel_editable_layer(),w.status.text()
        assert w.model.parts[0]['image'].getpixel((40,50))[3] == 255
        assert c.handle_layer_picker.isEnabled()
    finally:
        w.close()
