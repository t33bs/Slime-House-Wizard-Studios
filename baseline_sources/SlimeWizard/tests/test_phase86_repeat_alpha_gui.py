"""Windows PySide6 gate: move a translucent source after an opaque first move.

Tests normal user flow on the same pose without restarting Slimer, even when
first move was resized; unsafe multi-layer compositing must still be refused.
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest

# Test Suite windows must never trigger hidden recovery dialogs or touch actual backups.
pytestmark = pytest.mark.usefixtures("isolate_gui_recovery")
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def make_window():
    app=QApplication.instance() or QApplication([])
    w=Suite()
    w.confirm_unsaved_projects=lambda *args,**kwargs: True
    w.resize(1400,900)
    w.show()
    app.processEvents()
    return w


def test_first_opaque_then_isolated_translucent_move_original_same_pose():
    w=make_window()
    try:
        base=Image.new('RGBA',(128,128))
        for x in (25,26,27):
            for y in (60,61,62):
                base.putpixel((x,y),(220,80,30,255))
        base.putpixel((70,85),(110,225,60,132))
        base.putpixel((71,85),(80,220,120,255))
        w.model.import_part('Swordcat source',base)
        w.assets.addItem('Swordcat source');w.assets.setCurrentRow(0)
        w.slimer_toggle.setChecked(True)
        frames=len(w.model.animations.get(w.anim.currentText(), []))
        assert w.slimer_move_original.isChecked()
        # First edit: opaque leg scaled up, then applied.
        for x in (25,26,27):
            for y in (60,61,62): w.slimer_paint(x,y,False)
        assert w.slimer_create_editable_layer(),w.status.text()
        w.slimer_scale.setValue(150)
        assert w.slimer_apply_move_to_pose(),w.status.text()
        assert w.assets.currentRow()==0
        assert w.canvas.slimer_active and not w.canvas.asset_controls_enabled
        assert w.slimer_selection.mask.getbbox() is None
        # Second edit: partially-transparent edge and neighbouring opaque
        # source pixels on the same pose, no Slimer toggle or new frame.
        for xy in ((70,85),(71,85)): w.slimer_paint(*xy,False)
        assert w.slimer_create_editable_layer(),w.status.text()
        assert w._slimer_pending_move_original is True
        w._slimer_pending_part['x']=4
        assert w.slimer_apply_move_to_pose(),w.status.text()
        assert w.model.render().getpixel((70,85))[3] == 0
        assert w.model.render().getpixel((74,85)) == (110,225,60,132)
        assert w.model.render().getpixel((75,85)) == (80,220,120,255)
        assert len(w.model.animations.get(w.anim.currentText(), [])) == frames
        assert w.canvas.slimer_active and not w.canvas.asset_controls_enabled
    finally:
        w.close()


def test_translucent_overlay_compositing_remains_blocked_with_diagnostics():
    w=make_window()
    try:
        bottom=Image.new('RGBA',(128,128))
        bottom.putpixel((40,40),(50,220,70,255))
        top=Image.new('RGBA',(128,128))
        top.putpixel((40,40),(230,55,90,144))
        w.model.import_part('bottom',bottom)
        w.assets.addItem('bottom')
        w.model.import_part('translucent overlay',top)
        w.assets.addItem('translucent overlay')
        w.assets.setCurrentRow(1)
        w.slimer_toggle.setChecked(True)
        before=w.model.render().tobytes()
        w.slimer_paint(40,40,False)
        assert not w.slimer_create_editable_layer()
        assert 'multi-layer=1' in w.status.text()
        assert w.model.render().tobytes()==before
        assert w._slimer_pending_part is None
    finally:
        w.close()
