"""Windows PySide6 acceptance: visible Asset Library Import and Export for SHS."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication, QFileDialog
from friendly_animator import Suite


def _window():
    app=QApplication.instance() or QApplication([])
    w=Suite();w.confirm_unsaved_projects=lambda *a,**kw: True
    return app,w


def test_import_export_png_lossless_and_buttons_under_library(monkeypatch,tmp_path):
    _,w=_window()
    try:
        assert w.library_import.text()=='Import Asset'
        assert w.library_export_shs.text()=='Export for SHS'
        assert w.library_import.isEnabled() and w.library_export_shs.isEnabled()
        src=Image.new('RGBA',(12,14),(0,0,0,0))
        src.putpixel((3,4),(40,200,90,117))
        incoming=tmp_path/'swordcat_leg.png';src.save(incoming)
        monkeypatch.setattr(QFileDialog,'getOpenFileNames',lambda *a,**kw:([str(incoming)],'PNG'))
        w.library_import.click()
        assert w.assets.count()==1,w.status.text()
        assert w.selected==0
        assert w.model.originals[0].size==(12,14)
        assert w.model.originals[0].getpixel((3,4))==(40,200,90,117)
        outgoing=tmp_path/'shs_source.png'
        monkeypatch.setattr(QFileDialog,'getSaveFileName',lambda *a,**kw:(str(outgoing),'PNG'))
        w.library_export_shs.click()
        assert outgoing.exists(),w.status.text()
        with Image.open(outgoing) as asset:
            assert asset.size==(12,14)
            assert asset.convert('RGBA').tobytes()==src.tobytes()
        assert len(w.model.parts)==1
    finally:
        w.close()


def test_import_and_export_blocked_during_pending_layer(monkeypatch,tmp_path):
    _,w=_window()
    try:
        original=Image.new('RGBA',(128,128));original.putpixel((25,25),(210,60,40,255))
        w.model.import_part('Leg',original);w.assets.addItem('Leg')
        w.slimer_toggle.setChecked(True)
        w.slimer_paint(25,25,False)
        assert w.slimer_create_editable_layer(),w.status.text()
        n=w.assets.count()
        monkeypatch.setattr(QFileDialog,'getOpenFileNames',lambda *a,**kw:pytest.fail('Import dialog must not open while pending'))
        monkeypatch.setattr(QFileDialog,'getSaveFileName',lambda *a,**kw:pytest.fail('Export dialog must not open while pending'))
        w.library_import.click()
        assert w.assets.count()==n
        assert 'Apply Move or Cancel' in w.status.text()
        w.library_export_shs.click()
        assert 'Apply Move or Cancel' in w.status.text()
        assert w._slimer_pending_part is w.model.parts[-1]
    finally:
        w.close()


def test_import_during_slimer_highlight_refreshes_snapshot(monkeypatch,tmp_path):
    _,w=_window()
    try:
        w.slimer_toggle.setChecked(True)
        img=Image.new('RGBA',(128,128));img.putpixel((20,20),(255,50,120,255))
        file=tmp_path/'new_part.png';img.save(file)
        monkeypatch.setattr(QFileDialog,'getOpenFileNames',lambda *a,**kw:([str(file)],'PNG'))
        w.library_import.click()
        assert w.slimer_selection is not None
        assert w.slimer_selection.source.tobytes()==w.model.render().tobytes()
        w.slimer_paint(20,20,False)
        assert w.slimer_create_editable_layer(),w.status.text()
    finally:
        w.close()
