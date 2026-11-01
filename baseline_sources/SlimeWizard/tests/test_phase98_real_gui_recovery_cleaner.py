"""Windows Qt gate: repeat the user's two-move sequence across autosave ticks."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytestmark = pytest.mark.usefixtures('isolate_gui_recovery')
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from studio.pet_suite_model import PetSuiteModel
from friendly_animator import Suite


def _window():
    app=QApplication.instance() or QApplication([])
    w=Suite()
    w.confirm_unsaved_projects=lambda *a, **k: True
    w.show();app.processEvents()
    return w


def _move(w, x, y, dx):
    w.slimer_paint(x,y,False)
    w.slimer_edit_asset.click()
    assert w._slimer_pending_part is not None,w.status.text()
    w._slimer_pending_part['x']=dx
    w.slimer_apply_move.click()
    assert w._slimer_pending_part is None,w.status.text()


def test_recovery_timer_cannot_steal_two_leg_moves_into_earlier_pose(tmp_path):
    app=QApplication.instance() or QApplication([])
    w=_window()
    try:
        img=Image.new('RGBA',(128,128))
        img.putpixel((20,80),(200,30,30,255))
        img.putpixel((60,80),(30,30,200,255))
        w.model.import_part('Original Swordcat',img)
        w.assets.addItem('Original Swordcat');w.assets.setCurrentRow(0)
        w.slimer_toggle.setChecked(True)
        w.slimer_place_frame_button.click()
        animation=w.anim.currentText()
        original=w.model.render(w.model.animations[animation][0]).tobytes()
        source_layers=w.model.animations[animation][0]
        _move(w,20,80,4)
        # Reproduce the real ~60s recovery timer: do not write to disk here.
        w.project_is_dirty=lambda *args: False
        w.autosave_recovery()
        assert w.model.animations[animation][0] == source_layers
        assert w.model.render(w.model.animations[animation][0]).tobytes() == original
        _move(w,60,80,-5)
        w.autosave_recovery()
        assert w.model.render(w.model.animations[animation][0]).tobytes() == original
        w.slimer_place_frame_button.click()
        assert len(w.model.animations[animation])==2,w.status.text()
        assert w.model.render(w.model.animations[animation][0]).tobytes()==original
        second=w.model.render(w.model.animations[animation][1]).tobytes()
        assert second != original
        assert w.model.render(w.model.animations[animation][1]).getpixel((24,80)) == (200,30,30,255)
        assert w.model.render(w.model.animations[animation][1]).getpixel((55,80)) == (30,30,200,255)
        w.timeline.setCurrentRow(0);app.processEvents()
        assert w.model.render().tobytes()==original
        w.timeline.setCurrentRow(1);app.processEvents()
        assert w.model.render().tobytes()==second
        path=tmp_path/'sprite.rig.json'
        w.model.save_project(path)
        reloaded=PetSuiteModel.load_project(path)
        assert reloaded.render(reloaded.animations[animation][0]).tobytes()==original
        assert reloaded.render(reloaded.animations[animation][1]).tobytes()==second
    finally:w.close()


def test_cleaner_on_combined_artwork_after_place_frame_keeps_earlier_poses():
    w=_window()
    try:
        img=Image.new('RGBA',(128,128))
        img.putpixel((20,80),(200,30,30,255))
        img.putpixel((60,80),(30,30,200,255))
        w.model.import_part('Original Source',img)
        w.assets.addItem('Original Source');w.assets.setCurrentRow(0)
        w.slimer_toggle.setChecked(True)
        w.slimer_place_frame_button.click()
        name=w.anim.currentText()
        pose1=w.model.render(w.model.animations[name][0]).tobytes()
        _move(w,20,80,4)
        w.slimer_place_frame_button.click()
        assert w.frame==1
        pose2=w.model.render(w.model.animations[name][1]).tobytes()
        # Newly-created combined source is a real editable layer, too.
        assert any(s['name'].startswith('Combined Artwork') and s['visible']
                   for s in w.model.animations[name][1])
        w.slimer_toggle.setChecked(False)
        w.cleaner_toggle.setChecked(True)
        assert w.canvas.cleaner_active
        w.cleaner_start_stroke()
        w.cleaner_paint(24,80)
        assert w.model.render().getpixel((24,80))[3]==0
        assert w.model.render(w.model.animations[name][0]).tobytes()==pose1
        assert w.model.render(w.model.animations[name][1]).tobytes()==pose2
        w.autosave_recovery=lambda: w.preserve_pose_draft()
        w.autosave_recovery()
        assert w.model.render(w.model.animations[name][1]).tobytes()==pose2
        w.slimer_place_frame_button.click()
        assert len(w.model.animations[name])==3
        assert w.model.render(w.model.animations[name][1]).tobytes()==pose2
        assert w.model.render(w.model.animations[name][2]).getpixel((24,80))[3]==0
    finally:w.close()
