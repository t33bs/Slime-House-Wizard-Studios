"""Windows regression for real-world second highlight and clean handle reset."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest

# Test Suite windows must never trigger hidden recovery dialogs or touch actual backups.
pytestmark = pytest.mark.usefixtures("isolate_gui_recovery")
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_two_distinct_source_leg_edits_return_focus_and_hide_handles():
    app = QApplication.instance() or QApplication([])
    w = Suite()
    w.confirm_unsaved_projects = lambda *a, **k: True
    try:
        base = Image.new('RGBA', (128,128))
        base.putpixel((18,35), (231,50,50,255))
        base.putpixel((25,35), (210,180,55,255))
        base.putpixel((60,70), (170,20,220,255))
        w.model.import_part('Swordcat source', base)
        w.assets.addItem('Swordcat source')
        w.assets.setCurrentRow(0)
        w.slimer_toggle.setChecked(True)
        frames = len(w.model.animations.get(w.anim.currentText(), []))
        assert w.slimer_move_original.isChecked()
        for source_xy,dx in [((18,35),8), ((25,35),10)]:
            w.slimer_start_stroke()
            w.slimer_paint(*source_xy, False)
            assert w.slimer_create_editable_layer(), w.status.text()
            pending = w._slimer_pending_part
            assert pending is not None
            pending['x'] = dx
            assert w.slimer_apply_move_to_pose(), w.status.text()
            assert w.selected == 0, 'After Apply, source layer should be selected again'
            assert w.assets.currentRow() == 0
            assert w.canvas.asset_controls_enabled is False
            assert w.canvas.slimer_active
            assert w.slimer_selection.mask.getbbox() is None
            assert w.canvas.slimer_bounds is None
            assert w.model.render().getpixel(source_xy)[3] == 0
            assert w.model.render().getpixel((source_xy[0]+dx, source_xy[1]))[3] == 255
        assert len(w.model.parts) == 3
        assert len(w.model.animations.get(w.anim.currentText(), [])) == frames
    finally:
        w.close()


def test_translucent_second_highlight_stays_safe_and_explains_recovery():
    app = QApplication.instance() or QApplication([])
    w = Suite(); w.confirm_unsaved_projects = lambda *a, **k: True
    try:
        base=Image.new('RGBA',(128,128))
        base.putpixel((10,10),(220,30,20,255))
        base.putpixel((35,35),(15,190,65,140))
        w.model.import_part('Swordcat source',base)
        w.assets.addItem('Swordcat source')
        # A second fractional-alpha layer at (35,35) produces genuinely
        # ambiguous flattened pixels. This must still be rejected.
        shading=Image.new('RGBA',(128,128))
        shading.putpixel((35,35),(150,40,80,90))
        w.model.import_part('separate shading',shading)
        w.assets.addItem('separate shading');w.assets.setCurrentRow(0)
        w.slimer_toggle.setChecked(True)
        w.slimer_paint(10,10,False)
        assert w.slimer_create_editable_layer(),w.status.text()
        w._slimer_pending_part['x']=5
        assert w.slimer_apply_move_to_pose(),w.status.text()
        # This is a separate, genuinely translucent pixel.  The existing
        # opaque-source erasure rule must NOT silently erase it.
        w.slimer_paint(35,35,False)
        before=w.model.render().tobytes();count=len(w.model.parts)
        assert not w.slimer_create_editable_layer()
        assert w._slimer_pending_part is None
        assert len(w.model.parts)==count
        assert w.model.render().tobytes()==before
        assert 'Clear Selection' in w.status.text()
        assert w.canvas.slimer_active
    finally:
        w.close()
