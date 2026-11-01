"""Windows Qt GUI: exact vs over-previous PNG imports never cross-pollute poses.

Uses isolated recovery fixture so an invisible crash-recovery modal cannot
block CI and test windows cannot delete a real user's autosave data.
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
pytestmark = pytest.mark.usefixtures('isolate_gui_recovery')
pytest.importorskip('PySide6')
from PIL import Image
from PySide6.QtWidgets import QApplication, QFileDialog, QToolButton
from friendly_animator import Suite


def _window():
    app=QApplication.instance() or QApplication([])
    w=Suite()
    w.confirm_unsaved_projects=lambda *a,**k:True
    w.show();app.processEvents()
    return app,w


def _make_base(w):
    name=w.anim.currentText()
    art=Image.new('RGBA',w.model.size)
    art.putpixel((9,10),(0,0,0,255))
    art.putpixel((10,10),(220,70,30,255))
    art.putpixel((11,10),(20,20,20,80))
    w.model.import_part('Swordcat original',art)
    w.assets.addItem('Swordcat original')
    w.assets.setCurrentRow(0)
    w.model.insert_frame(name,0)
    w.select_timeline_pose(0)
    return name


def _write_png(tmp_path):
    image=Image.new('RGBA',(128,128))
    image.putpixel((9,10),(0,0,0,0))
    image.putpixel((10,10),(0,0,0,255))
    image.putpixel((11,10),(0,0,0,120))
    image.putpixel((12,10),(2,5,8,255))
    png=tmp_path/'Swordcat_Walk_Pose_1_128.png'
    image.save(png)
    return png,image


def test_exact_png_does_not_make_other_pose_black_transparent(tmp_path, monkeypatch):
    app,w=_window()
    try:
        animation=_make_base(w)
        before=w.model.render(w.model.animations[animation][0]).tobytes()
        old_states=w.model.animations[animation][0]
        old_id=w.model.pose_id(animation,0)
        path,source=_write_png(tmp_path)
        monkeypatch.setattr(QFileDialog,'getOpenFileName',lambda *a,**kw:(str(path),'PNG images (*.png)'))
        assert isinstance(w.pose_png_import_button,QToolButton)
        assert w.pose_png_import_button.menu() is not None
        w.import_pose_png()
        assert len(w.model.animations[animation])==2
        assert w.model.render(w.model.animations[animation][1]).tobytes()==source.tobytes()
        assert w.model.render(w.model.animations[animation][0]).tobytes()==before
        assert w.model.pose_id(animation,0)==old_id
        assert len(old_states)==1
        # New pose shows only its imported asset. Old source is untouched and
        # is still accessible by toggling the explicit inactive-layers option.
        assert [i for i in range(w.assets.count()) if not w.assets.item(i).isHidden()]==[1]
        w.show_hidden_assets.setChecked(True)
        assert [i for i in range(w.assets.count()) if not w.assets.item(i).isHidden()]==[0,1]
        w.show_hidden_assets.setChecked(False)
        w.select_timeline_pose(0)
        assert w.model.render().tobytes()==before
        assert not w.assets.item(0).isHidden()
        w.select_timeline_pose(1)
        assert w.model.render().tobytes()==source.tobytes()
        assert 'opaque black in PNG: 1 px' in w.status.text() or w.model.originals[-1].getpixel((10,10))==(0,0,0,255)
    finally:
        w.close()


def test_import_over_previous_reveals_base_and_preserves_first_pose(tmp_path, monkeypatch):
    app,w=_window()
    try:
        animation=_make_base(w)
        original=w.model.render(w.model.animations[animation][0]).tobytes()
        path,imported=_write_png(tmp_path)
        monkeypatch.setattr(QFileDialog,'getOpenFileName',lambda *a,**kw:(str(path),'PNG images (*.png)'))
        w.import_pose_png_overlay()
        assert len(w.model.animations[animation])==2
        composite=w.model.render(w.model.animations[animation][1])
        assert composite.getpixel((9,10))==(0,0,0,255)  # base remains under alpha=0
        assert composite.getpixel((10,10))==(0,0,0,255) # top opaque black
        assert w.model.render(w.model.animations[animation][0]).tobytes()==original
        assert [i for i in range(w.assets.count()) if not w.assets.item(i).isHidden()]==[1]
        assert 'over the previous pose' in w.status.text()
        # Changing new working layer does not alter previous saved pose.
        w.model.originals[1].putpixel((9,10),(255,255,255,255))
        w.model.parts[1]['image'].putpixel((9,10),(255,255,255,255))
        w.preserve_pose_draft()
        w.select_timeline_pose(0)
        assert w.model.render().tobytes()==original
        w.select_timeline_pose(1)
        assert w.model.render().getpixel((9,10))==(255,255,255,255)
    finally:
        w.close()
