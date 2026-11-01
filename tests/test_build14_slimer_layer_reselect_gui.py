"""Windows acceptance test for selecting the first of two confirmed Slimer moves."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtCore import Qt, QPoint
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from shws_wizard.friendly_animator import Suite


def test_two_real_slimer_edits_reselect_first_and_drag_without_switching():
    app=QApplication.instance() or QApplication([])
    w=Suite()
    w.confirm_unsaved_projects=lambda *_args,**_kwargs: True
    w.show();app.processEvents()
    try:
        source=Image.new('RGBA',(128,128))
        source.putpixel((12,12),(240,30,30,255))
        source.putpixel((70,70),(40,40,230,255))
        w.model.import_part('source',source)
        w.assets.addItem('source')
        w.assets.setCurrentRow(0)
        w.slimer_toggle.setChecked(True)
        moves=[]
        for x,y,shift in ((12,12,6),(70,70,3)):
            w.slimer_paint(x,y,False)
            assert w.slimer_create_editable_layer(),w.status.text()
            idx=w.selected
            moves.append(idx)
            w.canvas.moved.emit(shift,0)
            assert w.slimer_apply_move_to_pose(),w.status.text()
        one,two=moves
        assert one!=two
        second_at=(w.model.parts[two]['x'],w.model.parts[two]['y'])
        w.assets.setCurrentRow(one)
        assert w.selected==one
        assert w.slimer_create_editable_layer(),w.status.text() # Show handles, no new layer.
        assert w.canvas.asset_controls_enabled
        assert not w.canvas.slimer_active
        assert w._slimer_pending_part is None
        scale,ox,oy=w.canvas._geometry()
        pos=QPoint(round(ox+18.5*scale),round(oy+12.5*scale))
        assert 0<=pos.x()<w.canvas.width() and 0<=pos.y()<w.canvas.height()
        QTest.mousePress(w.canvas,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier,pos)
        assert w.selected==one, 'Clicking first Slimer move must not select Move 2'
        assert w.canvas._action=='move'
        w.canvas.moved.emit(5,0)
        QTest.mouseRelease(w.canvas,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.NoModifier,pos)
        assert w.selected==one
        assert (w.model.parts[two]['x'],w.model.parts[two]['y'])==second_at
        assert w.model.render().getpixel((23,12))==(240,30,30,255)
        assert w.model.render().getpixel((73,70))==(40,40,230,255)
    finally:
        w.close()
