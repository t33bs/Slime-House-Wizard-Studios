"""Windows Qt: Open Creature recognizes a plain JSON animation with real PNG."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
import shws_wizard.friendly_animator as wizard
from shws_wizard.studio.pet_suite_model import PetSuiteModel


def test_gui_opens_plain_sheet_json_as_independent_unsaved_editable_poses(tmp_path, monkeypatch):
    app=QApplication.instance() or QApplication([])
    model=PetSuiteModel((96,64))
    model.import_part('Art',Image.new('RGBA',(6,6),(20,80,180,255)))
    for n in range(9):
        model.parts[0]['x']=n*3
        model.save_frame('Walk')
        model.set_frame_duration('Walk',n,100+n*10)
    original=[model.render(p).tobytes() for p in model.animations['Walk']]
    model.export(tmp_path,'walk')
    path=tmp_path/'walk_sheet.json'
    monkeypatch.setattr(wizard.QFileDialog,'getOpenFileName',
                        lambda *a, **k:(str(path),'Creature or animation JSON (*.rig.json *.json)'))
    window=wizard.Suite()
    window.confirm_unsaved_projects=lambda *_a,**_k: True
    window.show();app.processEvents()
    try:
        count=len(window._projects)
        window.open_project();app.processEvents()
        assert len(window._projects)==count+1
        assert window.model.size==(96,64)
        assert window.timeline.count()==9
        assert window._project_paths.get(window._active_project_id) is None
        assert len(set(window.model.pose_ids['Walk']))==9
        assert [window.model.render(p).tobytes() for p in window.model.animations['Walk']]==original
        for index in (0,4,8):
            window.select_timeline_pose(index);app.processEvents()
            assert window.model.render().tobytes()==original[index]
    finally:
        window.close()
