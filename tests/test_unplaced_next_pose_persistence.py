"""Build 1.1: Save Creature must not require an additional placed frame."""
from copy import deepcopy
from pathlib import Path
import json
import pytest
from PIL import Image, ImageDraw
from shws_wizard.studio.pet_suite_model import PetSuiteModel
from shws_wizard.studio.project_validation import InvalidProjectDataError


def make_model(pose_count):
    m = PetSuiteModel((128,128))
    source = Image.new('RGBA',(12,12),(0,0,0,0))
    ImageDraw.Draw(source).rectangle((1,1,10,10),fill=(221,65,97,255))
    m.import_part('Creature base',source)
    name=m.current
    for idx in range(pose_count):
        m.parts[0]['x'] = 3+idx
        m.parts[0]['y'] = 6+(idx%5)
        m.insert_frame(name,idx)
    return m, name


@pytest.mark.parametrize('pose_count',[1,6,7,12])
def test_save_unplaced_next_pose_restores_live_canvas_and_preserves_every_saved_pose(tmp_path,pose_count):
    m, name = make_model(pose_count)
    before=deepcopy(m.animations[name]);ids=m._sync_pose_ids(name)[:]
    signatures=[m.render(pose).tobytes() for pose in before]
    m.apply_pose(before[-1]);m.parts[0]['x']+=24
    m.parts[0]['y']+=7
    draft_image=m.render().tobytes()
    assert draft_image!=signatures[-1]
    m.unplaced_next_pose={'animation':name,'pose_id':ids[-1]}
    path=tmp_path/'creature.rig.json'
    m.save_project(path)
    data=json.loads(path.read_text(encoding='utf8'))
    assert len(data['animations'][name])==pose_count
    assert data['unplaced_next_pose']==m.unplaced_next_pose
    loaded=PetSuiteModel.load_project(path)
    assert loaded.unplaced_next_pose==m.unplaced_next_pose
    assert loaded.render().tobytes()==draft_image
    assert loaded._sync_pose_ids(name)==ids
    assert loaded.animations[name]==before
    assert all(loaded.render(p).tobytes()==b for p,b in zip(before,signatures))
    # Placing the saved draft creates one NEW pose only after explicit action.
    loaded.insert_frame(name,pose_count,loaded.snapshot())
    assert len(loaded.animations[name])==pose_count+1
    assert loaded.render(loaded.animations[name][-1]).tobytes()==draft_image
    assert loaded.animations[name][:-1]==before


def test_saving_without_pending_draft_leaves_original_format_and_frames(tmp_path):
    m,name=make_model(7)
    path=tmp_path/'regular.rig.json'
    m.save_project(path)
    assert 'unplaced_next_pose' not in json.loads(path.read_text())
    loaded=PetSuiteModel.load_project(path)
    assert loaded.unplaced_next_pose is None
    assert loaded.animations[name]==m.animations[name]


def test_bad_unplaced_owner_rejected_before_any_editor_mutation(tmp_path):
    m,name=make_model(7)
    m.unplaced_next_pose={'animation':name,'pose_id':m.pose_id(name,6)}
    path=tmp_path/'creature.rig.json';m.save_project(path)
    data=json.loads(path.read_text())
    for invalid in [{'animation':name,'pose_id':'missing'},
                    {'animation':'Not an animation','pose_id':m.pose_id(name,6)},
                    {'animation':name,'pose_id':5},
                    {'animation':name,'pose_id':m.pose_id(name,6),'other':42}]:
        data['unplaced_next_pose']=invalid
        path.write_text(json.dumps(data))
        with pytest.raises(InvalidProjectDataError,match='unplaced next pose'):
            PetSuiteModel.load_project(path)


def test_pending_draft_flag_is_in_project_fingerprint():
    m,name=make_model(2)
    before=m.content_fingerprint()
    m.unplaced_next_pose={'animation':name,'pose_id':m.pose_id(name,1)}
    assert m.content_fingerprint()!=before
    m.unplaced_next_pose=None
    assert m.content_fingerprint()==before


def test_gui_save_path_is_not_blocked_by_awaiting_place_frame():
    # Import-free structural check so this invariant runs on CI even without Qt.
    src=(Path(__file__).resolve().parents[1]/'shws_wizard/friendly_animator.py').read_text()
    method=src.split('    def save_project_by_id(self,project_id,force_new_path=False):',1)[1].split('    def close_creature_project(',1)[0]
    assert '_remember_unplaced_next_pose()' in method
    assert 'model.save_project(path)' in method
    assert 'Your next pose is not placed yet.' not in method
    assert "self.model.unplaced_next_pose = None" in src
