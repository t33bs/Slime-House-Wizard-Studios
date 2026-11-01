"""Windows/PySide6 acceptance tests for Phase 85 layer resizing + safety recovery."""
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
    w.confirm_unsaved_projects = lambda *a, **kw: True
    w.resize(1400, 900)
    w.show()
    app.processEvents()
    return app, w


def test_staged_slimer_layer_resizes_only_selected_pixels_then_applies_move_original():
    app, w = _window()
    try:
        base = Image.new('RGBA', (128,128))
        for x in range(40, 44):
            for y in range(40, 44):
                base.putpixel((x,y), (220, 40, 55, 255))
        w.model.import_part('Swordcat source', base)
        w.assets.addItem('Swordcat source')
        w.assets.setCurrentRow(0)
        w.slimer_toggle.setChecked(True)
        frames = len(w.model.animations.get(w.anim.currentText(), []))
        for x in range(40,44):
            for y in range(40,44):
                w.slimer_paint(x,y,False)
        assert w.slimer_create_editable_layer(), w.status.text()
        index = w.selected
        source_bytes = w.model.parts[0]['image'].tobytes()
        original_bbox = w.model.parts[index]['image'].getchannel('A').getbbox()
        assert original_bbox == (40,40,44,44)
        assert w.canvas.handle_mode_picker.count() == 4
        w.canvas.set_canvas_handle_mode('resize')
        assert w.canvas.asset_handle_mode == 'resize'
        assert w.canvas._asset_handle_screen('resize') is not None
        w.slimer_scale.setValue(150)
        assert w.model.parts[index]['image'].size == (128,128)
        assert w.model.parts[index]['image'].getchannel('A').getbbox() == (39,39,45,45)
        assert w.model.parts[0]['image'].tobytes() == source_bytes
        assert w.slimer_scale.value() == 150
        # A later percent must come from the same original artwork,
        # not from repeatedly resized raster data.
        w.slimer_scale.setValue(100)
        assert w.model.parts[index]['image'].getchannel('A').getbbox() == original_bbox
        w.slimer_scale.setValue(150)
        assert w.slimer_apply_move_to_pose(), w.status.text()
        assert not w.canvas.asset_controls_enabled
        assert len(w.model.animations.get(w.anim.currentText(), [])) == frames
        assert w.model.parts[0]['image'].getpixel((40,40))[3] == 0
        assert w.model.parts[index]['image'].getchannel('A').getbbox() == (39,39,45,45)
    finally:
        w.close()


def test_imported_asset_scales_with_existing_edit_selection_and_no_extra_layer():
    app, w = _window()
    try:
        image = Image.new('RGBA', (6,4), (60,200,80,255))
        w.model.import_part('Imported hat', image)
        w.assets.addItem('Imported hat')
        w.assets.setCurrentRow(0)
        w.slimer_toggle.setChecked(True)
        assert w.slimer_create_editable_layer(), w.status.text()
        assert w.canvas.asset_controls_enabled
        w.canvas.set_canvas_handle_mode('resize')
        w.slimer_scale.setValue(150)
        assert w.model.parts[0]['image'].size == (9,6)
        assert w.model.originals[0].size == (6,4)
        assert w.slimer_apply_move_to_pose(),w.status.text()
        assert len(w.model.parts) == 1
        assert not w.canvas.asset_controls_enabled
        assert w.model.parts[0]['image'].size == (9,6)
    finally:
        w.close()


def test_after_translucent_move_original_rejection_can_edit_entire_existing_source():
    app, w = _window()
    try:
        base = Image.new('RGBA', (128,128))
        base.putpixel((30,30), (255,80,60,255))
        base.putpixel((40,40), (170,100,40,145))
        w.model.import_part('Swordcat source', base)
        w.assets.addItem('Swordcat source')
        separate=Image.new('RGBA',(128,128))
        separate.putpixel((40,40),(45,225,20,120))
        w.model.import_part('overlapping translucent detail',separate)
        w.assets.addItem('overlapping translucent detail')
        w.assets.setCurrentRow(0)
        w.slimer_toggle.setChecked(True)
        w.slimer_paint(30,30,False)
        assert w.slimer_create_editable_layer(),w.status.text()
        w._slimer_pending_part['x'] = 10
        assert w.slimer_apply_move_to_pose(),w.status.text()
        w.slimer_paint(40,40,False)
        rendered = w.model.render().tobytes()
        assert not w.slimer_create_editable_layer()
        assert w.model.render().tobytes() == rendered
        assert 'multi-layer=1' in w.status.text()
        w.slimer_clear()
        w.assets.setCurrentRow(0)
        assert w.slimer_create_editable_layer(),w.status.text()
        assert w.canvas.asset_controls_enabled
        assert w._slimer_pending_part is None
        assert w.slimer_apply_move_to_pose(),w.status.text()
        assert not w.canvas.asset_controls_enabled
        assert w.model.parts[0]['image'].getpixel((40,40))[3] == 145
    finally:
        w.close()
