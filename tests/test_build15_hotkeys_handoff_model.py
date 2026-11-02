"""Build 1.5: keyboard routing and independent timeline PNG handoff contracts."""
import ast
from pathlib import Path

from PIL import Image
import pytest

from shws_wizard.studio.pet_suite_model import PetSuiteModel

ROOT = Path(__file__).resolve().parents[1]


def test_shortcuts_have_no_pencil_bucket_collision():
    shs = (ROOT/'studio/app.py').read_text(encoding='utf8')
    assert "('P',self.activate_universal_brush)" in shs
    assert "('B',self.activate_paint_bucket)" in shs
    assert "('B',self.activate_universal_brush)" not in shs
    assert "self.tool.setCurrentText('Paint Bucket')" in shs
    assert "('E',self.activate_universal_eraser)" in shs
    assert "('I',self.activate_eyedropper)" in shs
    assert 'P: Pencil' in shs and 'B: Paint Bucket' in shs


def test_both_save_buttons_use_one_success_only_return_path():
    shs = (ROOT/'studio/app.py').read_text(encoding='utf8')
    host = (ROOT/'main.py').read_text(encoding='utf8')
    wizard = (ROOT/'shws_wizard/friendly_animator.py').read_text(encoding='utf8')
    assert 'self._linked_png_save_callback=None' in shs
    assert 'callback(str(target.resolve()))' in shs
    assert 'self.studio._linked_png_save_callback = self._finish_shs_frame_handoff' in host
    assert "self.studio.external_save_button.setText('Save Back to Animator + Return to Wizard')" in host
    assert 'self.studio.save_external_png()' in host
    assert 'if not self.wizard.reload_shs_edit():' in host
    assert 'self.tabs.setCurrentWidget(self.wizard)' in host
    assert 'self.wizard._shs_edit = None' in host
    assert 'self._shs_pose_id = self.model.pose_id(animation, self.frame)' in host
    assert "self.model.pose_id(animation,index)!=expected_id" in wizard
    assert 'def reload_shs_edit(self):' in wizard
    # Verify emitted completion is inside successful safe_export's try branch.
    tree=ast.parse(shs)
    mw=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='MainWindow')
    save=next(n for n in mw.body if isinstance(n,ast.FunctionDef) and n.name=='save_external_png')
    guarded=next(n for n in ast.walk(save) if isinstance(n,ast.Try))
    successful=ast.unparse(guarded.body)
    assert 'safe_export(' in successful
    # No callback may run before the atomic PNG export has succeeded.
    assert 'callback(' not in successful
    body=ast.unparse(save.body)
    assert body.index('safe_export(') < body.index('callback(str(target.resolve()))')
    assert 'return True' in body
    assert 'return False' in ast.unparse(guarded.handlers)


@pytest.mark.parametrize('number_of_poses,target_index', [(1,0),(6,2),(7,6),(12,5)])
def test_replace_png_edits_one_existing_pose_without_creating_timeline_frames(tmp_path, number_of_poses, target_index):
    m=PetSuiteModel((128,128))
    image=Image.new('RGBA',(128,128))
    image.putpixel((7,7),(35,66,77,255))
    m.import_part('Creature',image)
    animation='Walk'
    for frame in range(number_of_poses):
        m.parts[0]['x']=frame
        m.save_frame(animation)
    ids=m._sync_pose_ids(animation)[:]
    before=[m.render(pose).tobytes() for pose in m.animations[animation]]
    timings=[m.frame_duration(animation,i) for i in range(number_of_poses)]
    edited=Image.new('RGBA',(128,128))
    edited.putpixel((30,40),(255,5,77,255))
    new_index=m.replace_frame_image(animation,target_index,edited)
    assert new_index==len(m.parts)-1
    assert len(m.animations[animation])==number_of_poses
    assert m._sync_pose_ids(animation)==ids
    assert [m.frame_duration(animation,i) for i in range(number_of_poses)]==timings
    for i,pose in enumerate(m.animations[animation]):
        if i==target_index:
            assert m.render(pose).tobytes()==edited.tobytes()
            assert pose[-1]['name']==f'Frame {i+1} PNG edit'
        else:
            assert m.render(pose).tobytes()==before[i]
    # Save/reopen must preserve the imported pose and all independent frames.
    project=tmp_path/'handed-back.rig.json'
    m.save_project(project)
    reopened=PetSuiteModel.load_project(project)
    assert len(reopened.animations[animation])==number_of_poses
    assert reopened._sync_pose_ids(animation)==ids
    assert [reopened.frame_duration(animation,i) for i in range(number_of_poses)]==timings
    assert reopened.render(reopened.animations[animation][target_index]).tobytes()==edited.tobytes()
    assert all(reopened.render(reopened.animations[animation][i]).tobytes()==before[i] for i in range(number_of_poses) if i!=target_index)
    # The user can undo an import using pose recovery, then re-edit independently.
    assert m.restore_previous_pose(animation,target_index)
    assert m.render(m.animations[animation][target_index]).tobytes()==before[target_index]


def test_reject_wrong_size_without_mutating_pose():
    m=PetSuiteModel((128,128))
    m.import_part('Creature',Image.new('RGBA',(128,128),'red'))
    animation='Walk';m.save_frame(animation)
    before=m.render(m.animations[animation][0]).tobytes()
    with pytest.raises(ValueError,match='canvas size'):
        m.replace_frame_image(animation,0,Image.new('RGBA',(64,64),'blue'))
    assert m.render(m.animations[animation][0]).tobytes()==before
    assert len(m.animations[animation])==1
