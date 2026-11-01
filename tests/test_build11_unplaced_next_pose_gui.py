"""Windows Qt acceptance: Save Creature without placing another timeline pose."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from shws_wizard.friendly_animator import Suite
from shws_wizard.studio.pet_suite_model import PetSuiteModel


def test_gui_save_creature_unplaced_pose_survives_reopen_and_seventh_frame(tmp_path):
    app=QApplication.instance() or QApplication([])
    w=Suite()
    w.confirm_unsaved_projects=lambda *_a,**_kw: True
    w.show()
    app.processEvents()
    try:
        original=Image.new('RGBA',(128,128))
        original.putpixel((20,20),(150,40,80,255))
        w.model.import_part('Creature',original)
        w.assets.addItem('Creature')
        w.assets.setCurrentRow(0)
        name=w.anim.currentText()
        assert w.slimer_place_frame(),w.status.text() # Pose 1
        for index in range(1,7):
            w.model.parts[0]['x']+=2
            w.mark_pose_draft()
            w._next_pose_capture_pending=True
            assert w.slimer_place_frame(),w.status.text()
        assert len(w.model.animations[name])==7
        saved_pose_pixels=[w.model.render(pose).tobytes() for pose in w.model.animations[name]]
        saved_pose_ids=w.model._sync_pose_ids(name)[:]
        w.model.parts[0]['x']+=3
        w.mark_pose_draft()
        w._next_pose_capture_pending=True
        draft_pixels=w.model.render().tobytes()
        assert draft_pixels!=saved_pose_pixels[-1]
        saved=tmp_path/'save-without-place.rig.json'
        w._project_paths[w._active_project_id]=str(saved)
        assert w.save_project_by_id(w._active_project_id),w.status.text()
        assert saved.is_file()
        assert len(w.model.animations[name])==7
        assert [w.model.render(p).tobytes() for p in w.model.animations[name]]==saved_pose_pixels
        model=PetSuiteModel.load_project(saved)
        assert model.render().tobytes()==draft_pixels
        assert model._sync_pose_ids(name)==saved_pose_ids
        # Reopening in the actual GUI must NOT apply the previously saved
        # pose over the live unplaced next-pose artwork.
        w.add_project(model,'Reopened with draft',saved)
        app.processEvents()
        assert w._next_pose_capture_pending
        assert w.timeline.count()==7
        assert w.frame==6
        assert w.model.render().tobytes()==draft_pixels
        # Re-clicking the selected timeline thumbnail must not destroy draft.
        w.load_frame(6)
        assert w.model.render().tobytes()==draft_pixels
        assert w._next_pose_capture_pending
        assert w.slimer_place_frame(),w.status.text()
        assert len(w.model.animations[name])==8
        assert [w.model.render(p).tobytes() for p in w.model.animations[name][:7]]==saved_pose_pixels
        assert w.model.render(w.model.animations[name][7]).tobytes()==draft_pixels
    finally:
        w.close()
