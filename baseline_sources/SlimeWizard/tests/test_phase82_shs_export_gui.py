"""Windows Qt acceptance: Export for SHS actually writes selected visible artwork."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication, QFileDialog
from friendly_animator import Suite


def _window():
    app=QApplication.instance() or QApplication([])
    window=Suite()
    window.confirm_unsaved_projects=lambda *a,**kw: True
    return app,window


def test_shs_export_button_creates_visible_png_for_transformed_slimer_layer(monkeypatch,tmp_path):
    _,w=_window()
    try:
        image=Image.new('RGBA',(128,128))
        for y in range(102,110):
            for x in range(23,28):
                image.putpixel((x,y),(45,145,220,255))
        w.model.import_part('Slimer Layer 001',image)
        w.assets.addItem('Slimer Layer 001')
        w.assets.setCurrentRow(0)
        # The selected layer can move without a new pose/frame.
        w.model.parts[0]['x']=7
        w.model.parts[0]['y']=-3
        outfile=tmp_path/'slimer_asset.png'
        monkeypatch.setattr(QFileDialog,'getSaveFileName',lambda *a,**kw:(str(outfile),'PNG'))
        w.library_export_shs.click()
        assert outfile.is_file(),w.status.text()
        with Image.open(outfile) as saved:
            saved.load()
            assert saved.format=='PNG'
            assert saved.size==(5,8),saved.size
            assert saved.convert('RGBA').getpixel((0,0))==(45,145,220,255)
        assert '5 x 8' in w.status.text()
    finally:
        w.close()


def test_shs_export_button_warns_instead_of_saving_empty_image(monkeypatch,tmp_path):
    _,w=_window()
    try:
        empty=Image.new('RGBA',(128,128))
        w.model.import_part('Empty layer',empty)
        w.assets.addItem('Empty layer')
        w.assets.setCurrentRow(0)
        monkeypatch.setattr(QFileDialog,'getSaveFileName',lambda *a,**kw:pytest.fail('No save dialog for a blank layer'))
        w.library_export_shs.click()
        assert 'no visible pixels' in w.status.text() or 'no source pixels' in w.status.text()
    finally:
        w.close()
