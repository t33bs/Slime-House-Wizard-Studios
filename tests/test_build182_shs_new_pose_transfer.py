"""Build 1.8.2 new-pose handoff tests; real Wizard method isolated from Qt."""
import ast
from pathlib import Path
from types import SimpleNamespace

from PIL import Image
import pytest

from shws_wizard.studio.pet_suite_model import PetSuiteModel

ROOT=Path(__file__).resolve().parents[1]


def wizard_import_function():
    source=(ROOT/'shws_wizard/friendly_animator.py').read_text(encoding='utf8')
    module=ast.parse(source)
    suite=next(c for c in module.body if isinstance(c, ast.ClassDef) and c.name=='Suite')
    method=next(m for m in suite.body if isinstance(m, ast.FunctionDef) and m.name=='import_shs_image_as_new_pose')
    warning=SimpleNamespace(information=lambda *a, **k: None, warning=lambda *a, **k: None)
    ns={'Image':Image, 'QMessageBox':warning}
    exec(compile(ast.Module(body=[method],type_ignores=[]),'<actual wizard method>','exec'),ns)
    return ns['import_shs_image_as_new_pose']


class FakeWizard:
    def __init__(self, count, index):
        self.model=PetSuiteModel((128,128))
        self.anim=SimpleNamespace(currentText=lambda:'Idle / Breathing')
        self.frame=index
        self.model.current='Idle / Breathing'
        self.model.animations.setdefault('Idle / Breathing', [])
        art=Image.new('RGBA',(128,128),(0,0,0,0))
        art.putpixel((13,14),(252,8,10,255))
        self.model.import_part('Swordcat',art)
        for i in range(count):
            self.model.parts[0]['x']=i
            self.model.save_frame('Idle / Breathing')
        if count:
            self.model.apply_pose(self.model.animations['Idle / Breathing'][index])
        self._slimer_pending_part=None
        self._slimer_pending_layer=None
        self._next_pose_capture_pending=False
        self._pose_draft_key=None
        self._pose_draft_dirty=False
        self.assets=SimpleNamespace(addItem=lambda *_:None)
        self.status=SimpleNamespace(setText=lambda *_:None)
        self.was_remembered=False

    def _canvas_owns_selected_pose(self,animation):
        return True
    def preserve_pose_draft(self):
        pass
    def remember(self):
        self.was_remembered=True
    def _timeline_structure_changed(self):
        pass
    def select_timeline_pose(self,index):
        self.frame=index
        self.model.apply_pose(self.model.animations['Idle / Breathing'][index])


@pytest.mark.parametrize('count,index',[(0,0),(1,0),(6,2),(7,6),(12,4)])
def test_add_new_pose_preserves_original_frames_and_round_trip(count,index,tmp_path):
    w=FakeWizard(count,index)
    animation=w.anim.currentText()
    before_frames=w.model.animations[animation][:]
    before=[w.model.render(p).tobytes() for p in before_frames]
    ids=w.model._sync_pose_ids(animation)[:]
    timings=[w.model.frame_duration(animation,i) for i in range(count)]
    shs=Image.new('RGBA',(128,128),(0,0,0,0))
    shs.putpixel((63,61),(23,44,55,187))
    shs.putpixel((65,62),(255,80,8,255))
    assert wizard_import_function()(w,shs) is True
    expected_insert=min(index+1,count)
    assert w.frame==expected_insert
    assert len(w.model.animations[animation])==count+1
    assert w.model.pose_id(animation,expected_insert) not in ids
    assert [p for i,p in enumerate(w.model._sync_pose_ids(animation)) if i!=expected_insert]==ids
    after=[w.model.render(p).tobytes() for p in w.model.animations[animation]]
    assert after[expected_insert]==shs.tobytes()  # pixel-exact alpha; no flatten or rescale
    assert [p for i,p in enumerate(after) if i!=expected_insert]==before
    assert [w.model.frame_duration(animation,i) for i in range(count+1) if i!=expected_insert]==timings
    assert w.was_remembered
    filename=tmp_path/'imported.rig.json'
    w.model.save_project(filename)
    reopened=PetSuiteModel.load_project(filename)
    assert len(reopened.animations[animation])==count+1
    assert [reopened.render(p).tobytes() for p in reopened.animations[animation]]==after


@pytest.mark.parametrize('reason', ['pending-layer','pending-part','unplaced-next-pose','size-mismatch','invalid-image','wrong-owner'])
def test_transfer_rejects_unsafe_state_without_new_frame(reason):
    w=FakeWizard(6,2)
    before=w.model.content_fingerprint()
    if reason=='pending-layer': w._slimer_pending_layer=12
    if reason=='pending-part': w._slimer_pending_part=object()
    if reason=='unplaced-next-pose': w._next_pose_capture_pending=True
    if reason=='wrong-owner': w._canvas_owns_selected_pose=lambda *_:False
    image=Image.new('RGBA',(64,64)) if reason=='size-mismatch' else Image.new('RGBA',(128,128))
    if reason=='invalid-image': image=None
    assert wizard_import_function()(w,image) is False
    assert w.model.content_fingerprint()==before
    assert not w.was_remembered


def test_host_has_discoverable_shs_button_and_separate_linked_replace():
    host=(ROOT/'main.py').read_text(encoding='utf8')
    shs=(ROOT/'studio/app.py').read_text(encoding='utf8')
    assert "'Send to Slime Wizard as New Pose', sidebar)" in host
    assert 'sidebar_layout.insertWidget(' in host
    assert 'self.studio.send_new_pose_button.clicked.connect(self.send_shs_as_new_pose)' in host
    assert 'self.wizard.import_shs_image_as_new_pose(image)' in host
    assert 'self.studio.current_image().convert(\'RGBA\').copy()' in host
    assert 'self.studio.external_save_button.setVisible(False)' in host
    assert 'self.studio._linked_png_save_callback = self._finish_shs_frame_handoff' in host
    assert "self.studio.external_save_button.setText('Save Back to Animator + Return to Wizard')" in host
    assert 'self.studio.save_external_png()' in host
    assert 'def current_image(self):' in shs


def host_transfer_function():
    src=(ROOT/'main.py').read_text(encoding='utf8')
    module=ast.parse(src)
    host=next(c for c in module.body if isinstance(c,ast.ClassDef) and c.name=='SlimeHouseWizardStudios')
    method=next(m for m in host.body if isinstance(m,ast.FunctionDef) and m.name=='send_shs_as_new_pose')
    ns={'QMessageBox':SimpleNamespace(warning=lambda *_:None)}
    exec(compile(ast.Module(body=[method],type_ignores=[]),'<actual host method>','exec'),ns)
    return ns['send_shs_as_new_pose']


@pytest.mark.parametrize('accepted', [True,False])
def test_host_transfer_only_ends_existing_link_after_success(accepted):
    events=[]
    image=Image.new('RGBA',(128,128),(0,0,0,0))
    linked=object()
    studio=SimpleNamespace(
        current_image=lambda:image,
        external_png_path=linked,
        external_save_button=SimpleNamespace(setVisible=lambda visible:events.append(('linked_visible',visible))),
    )
    wizard=SimpleNamespace(
        import_shs_image_as_new_pose=lambda im:events.append(('transfer',im.tobytes())) or accepted,
        _shs_edit=('linked.png',42,'Idle / Breathing',2),
        _shs_pose_id='pose_id_before',
        frame=3,
        status=SimpleNamespace(setText=lambda status:events.append(('status',status))),
    )
    host=SimpleNamespace(studio=studio,wizard=wizard,
        tabs=SimpleNamespace(setCurrentWidget=lambda w:events.append(('tab','wizard'))))
    result=host_transfer_function()(host)
    assert result==accepted
    assert events[0]==('transfer',image.tobytes())
    if accepted:
        assert wizard._shs_edit is None
        assert wizard._shs_pose_id is None
        assert studio.external_png_path is None
        assert ('linked_visible',False) in events
        assert ('tab','wizard') in events
    else:
        assert wizard._shs_edit==('linked.png',42,'Idle / Breathing',2)
        assert wizard._shs_pose_id=='pose_id_before'
        assert studio.external_png_path is linked
        assert ('linked_visible',False) not in events
        assert ('tab','wizard') not in events
