"""Build 1.9.4: Cleaner pose ownership, first-change undo, and long-session stability."""
import ast
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

from PIL import Image
from shws_wizard.studio.pet_suite_model import PetSuiteModel
from shws_wizard.studio.edit_history import EditHistory
from shws_wizard.studio.slime_cleaner import erase_visible_pixels

WIZARD = Path(__file__).resolve().parents[1] / 'shws_wizard' / 'friendly_animator.py'


def suite_method(name):
    """Run real GUI method source without importing Qt on Linux."""
    root = ast.parse(WIZARD.read_text(encoding='utf-8'))
    suite = next(n for n in root.body if isinstance(n, ast.ClassDef) and n.name == 'Suite')
    method = deepcopy(next(n for n in suite.body if isinstance(n, ast.FunctionDef) and n.name == name))
    module = ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[]))
    env = {}
    exec(compile(module, str(WIZARD), 'exec'), env)
    return env[name]


def make_model(count=12):
    model=PetSuiteModel((128, 128))
    image=Image.new('RGBA',(128,128))
    image.putpixel((14,20),(235,20,20,255))
    image.putpixel((15,20),(230,180,45,255))
    model.import_part('Creature',image)
    name='Walk'
    for i in range(count):
        model.parts[0]['x']=i*3
        model.save_frame(name)
    model.current=name
    model.apply_pose(model.animations[name][0])
    return model,name


def poses(model,name):
    return [model.render(p).tobytes() for p in model.animations[name]]


def make_cleaner_editor(count=12):
    model,name=make_model(count)
    history=EditHistory()
    records=[]
    editor=SimpleNamespace(model=model,history=history,frame=5, _active_project_id=0,
        _pose_draft_key=(0,name,5,model.pose_id(name,5)),_pose_live_id=model.pose_id(name,5),
        _pose_draft_dirty=False,_next_pose_capture_pending=False,
        anim=SimpleNamespace(currentText=lambda:name),
        cleaner_brush=SimpleNamespace(value=lambda:1),
        status=SimpleNamespace(setText=lambda message:records.append(message)),
        refresh=lambda:None, _cleaner_resolved_states=lambda:editor.model.resolved_pose(),
        _canvas_owns_selected_pose=lambda key: key==name and editor._pose_live_id==model.pose_id(name,editor.frame),
        remember=lambda:history.record(model),mark_pose_draft=lambda:setattr(editor,'_pose_draft_dirty',True))
    editor._cleaner_record_first_change=lambda:suite_method('_cleaner_record_first_change')(editor)
    return editor,name,records


def test_cleaner_only_marks_edited_pose_and_never_starts_new_frame():
    e,name,_=make_cleaner_editor()
    target=e.frame
    e.model.apply_pose(e.model.animations[name][target])
    before=poses(e.model,name)
    before_ids=e.model._sync_pose_ids(name)[:]
    start=suite_method('cleaner_start_stroke')
    paint=suite_method('cleaner_paint')
    end=suite_method('cleaner_end_stroke')
    start(e)
    paint(e,14+target*3,20)
    paint(e,15+target*3,20)
    end(e)
    assert len(e.history.past)==1, 'two changes in one stroke must create exactly one undo step'
    assert not e._next_pose_capture_pending, 'Cleaner must not block timeline navigation'
    assert e._pose_draft_dirty
    # The normal pose-draft preservation writes only to the verified pose.
    e.model.save_pose_at(name,target)
    after=poses(e.model,name)
    assert before[target]!=after[target]
    assert all(a==b for i,(a,b) in enumerate(zip(before,after)) if i!=target)
    assert e.model._sync_pose_ids(name)==before_ids
    assert len(set(after))==12, 'timeline must retain distinct pose appearances'
    assert e.history.undo(e.model)
    assert poses(e.model,name)==before


def test_empty_cleaner_click_neither_consumes_memory_nor_clears_redo():
    e,name,_=make_cleaner_editor()
    e.model.apply_pose(e.model.animations[name][e.frame])
    e.history.future.append({'sentinel':'redo'})
    suite_method('cleaner_start_stroke')(e)
    suite_method('cleaner_paint')(e,127,127)
    suite_method('cleaner_end_stroke')(e)
    assert not e.history.past
    assert e.history.future==[{'sentinel':'redo'}]
    assert not e._pose_draft_dirty
    assert not e._next_pose_capture_pending


def test_mismatched_pose_blocks_cleaner_without_pixel_loss():
    e,name,notices=make_cleaner_editor()
    e.model.apply_pose(e.model.animations[name][e.frame])
    baseline=e.model.snapshot()
    e._pose_live_id='wrong-id'
    suite_method('cleaner_start_stroke')(e)
    suite_method('cleaner_paint')(e,14+e.frame*3,20)
    suite_method('cleaner_end_stroke')(e)
    assert baseline==e.model.snapshot()
    assert not e.history.past
    assert any('blocked' in note.lower() for note in notices)


def test_genuine_pending_slimer_draft_survives_cleaner():
    e,name,_=make_cleaner_editor()
    e.model.apply_pose(e.model.animations[name][e.frame])
    e._next_pose_capture_pending=True
    before=poses(e.model,name)
    suite_method('cleaner_start_stroke')(e)
    suite_method('cleaner_paint')(e,14+e.frame*3,20)
    suite_method('cleaner_end_stroke')(e)
    assert e._next_pose_capture_pending is True
    assert poses(e.model,name)==before, 'unplaced draft must not overwrite a saved pose'


def test_callback_first_change_only_and_noop():
    parts=[{'image':Image.new('RGBA',(8,8)), 'x':0,'y':0,'visible':True}]
    called=[]
    before=lambda:called.append('record')
    assert not erase_visible_pixels(parts,1,1,before_first_change=before)
    assert called==[]
    parts[0]['image'].putpixel((1,1),(5,6,7,255))
    parts[0]['image'].putpixel((2,1),(1,2,3,255))
    assert erase_visible_pixels(parts,1,1,2,before_first_change=before)
    assert called==['record']


def test_undo_resets_stale_next_pose_flag_and_reloads_correct_canvas():
    method=suite_method('_after_history_restore')
    m,name=make_model(9)
    old=m.render(m.animations[name][4]).tobytes()
    class Selector:
        def __init__(self):self.name=name
        def blockSignals(self,value):return False
        def findText(self,value):return 0 if value==self.name else -1
        def currentText(self):return self.name
        def setCurrentText(self,value):self.name=value
        def addItem(self,value):self.name=value
    editor=SimpleNamespace(model=m,anim=Selector(),frame=4,
        _next_pose_capture_pending=True,_pose_draft_key=('stale',),_pose_draft_dirty=True,
        slimer_move_original=SimpleNamespace(setEnabled=lambda x:None),
        _reset_slimer_for_project_change=lambda:None,
        _after_history_change=lambda:None,
        _timeline_history_signature=lambda:'unchanged',
        _timeline_structure_changed=lambda:None)
    def load(index):
        # Mimic real load_frame's pending guard and model.apply_pose.
        if editor._next_pose_capture_pending:return
        editor.frame=index
        m.apply_pose(m.animations[name][index])
    editor.select_timeline_pose=load
    m.apply_pose(m.animations[name][0])
    method(editor,'unchanged',(name,m.pose_id(name,4),4))
    assert editor._next_pose_capture_pending is False
    assert editor.frame==4
    assert m.render().tobytes()==old, 'Undo must restore correct selected canvas'


def test_24_pose_navigation_and_50_cleaner_strokes_keep_independent_pixels():
    m,name=make_model(24)
    saved=poses(m,name)
    for i in range(50):
        target=i%24
        m.apply_pose(m.animations[name][target])
        # Alternate a true edit and a no-op over many navigation cycles.
        if i<24:
            x=14+target*3
            modified=set()
            history=EditHistory()
            changed=erase_visible_pixels(m.parts,x,20,states=m.resolved_pose(),canvas_size=m.size,
                  modified_indices=modified,before_first_change=lambda:history.record(m))
            assert changed and len(history.past)==1
            for part in modified:m.originals[part]=m.parts[part]['image'].copy()
            m.save_pose_at(name,target)
        assert len({m.pose_id(name,j) for j in range(24)})==24
    after=poses(m,name)
    assert all(x!=y for x,y in zip(saved,after))
    assert len(set(after))==24
