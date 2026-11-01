"""Windows acceptance: mouse-ready staged Move Original may overlap its source."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_overlapping_leg_move_keeps_destination_and_erases_only_original():
    app=QApplication.instance() or QApplication([])
    w=Suite();w.confirm_unsaved_projects=lambda *a,**kw: True
    try:
        image=Image.new('RGBA',(128,128))
        for y in range(30,34):
            for x in range(30,34):
                image.putpixel((x,y),(235,90,60,255))
        image.putpixel((80,80),(70,170,255,255))
        w.model.import_part('Swordcat leg', image)
        w.assets.addItem('Swordcat leg')
        w.assets.setCurrentRow(0)
        w.slimer_toggle.setChecked(True)
        assert w.slimer_move_original.isChecked()
        for y in range(30,34):
            for x in range(30,34): w.slimer_paint(x,y,False)
        assert w.slimer_create_editable_layer(),w.status.text()
        staged=w._slimer_pending_part
        staged['x']=1
        assert w.slimer_apply_move_to_pose(),w.status.text()
        assert staged['image'].getpixel((30,30))==(235,90,60,255)
        assert w.model.parts[0]['image'].getpixel((30,30))[3]==0
        assert w.model.render().getpixel((30,30))[3]==0
        for x in range(31,35):
            assert w.model.render().getpixel((x,30))==(235,90,60,255)
        assert w.model.render().getpixel((80,80))==(70,170,255,255)
        assert w._slimer_pending_part is None
        assert w.canvas.slimer_active
    finally:
        w.close()


def test_empty_highlight_edit_selection_keeps_brush_without_adding_layer():
    app=QApplication.instance() or QApplication([])
    w=Suite();w.confirm_unsaved_projects=lambda *a,**kw: True
    try:
        w.model.import_part('Swordcat',Image.new('RGBA',(128,128)))
        w.assets.addItem('Swordcat');w.assets.setCurrentRow(0)
        w.slimer_toggle.setChecked(True)
        n=w.assets.count()
        assert not w.slimer_create_editable_layer()
        assert 'Nothing highlighted' in w.status.text()
        assert w.canvas.slimer_active
        assert w.assets.count()==n
        assert w._slimer_pending_part is None
    finally:
        w.close()
