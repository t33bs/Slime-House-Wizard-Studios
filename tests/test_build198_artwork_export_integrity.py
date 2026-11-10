"""Build 1.9.8: never lose intentional detached pixels or silently skip Cleaner edits."""
import ast
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

from PIL import Image

from shws_wizard.studio.gif_export import encode_gif
from shws_wizard.studio.apng_export import encode_apng
from shws_wizard.studio.pet_suite_model import PetSuiteModel
from shws_wizard.studio.slime_cleaner import erase_visible_pixels

WIZARD = Path(__file__).resolve().parents[1] / 'shws_wizard' / 'friendly_animator.py'


def suite_method(name):
    root=ast.parse(WIZARD.read_text(encoding='utf-8'))
    suite=next(n for n in root.body if isinstance(n, ast.ClassDef) and n.name=='Suite')
    method=deepcopy(next(n for n in suite.body if isinstance(n,ast.FunctionDef) and n.name==name))
    env={}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])),str(WIZARD),'exec'),env)
    return env[name]


def make_editor():
    model=PetSuiteModel((16, 16))
    source=Image.new('RGBA',(16,16))
    source.putpixel((1, 1),(200,30,45,255))
    source.putpixel((15, 12),(75,188,255,40)) # disconnected artist pixel
    model.import_part('Swordcat wind',source)
    model.save_frame('Wind')
    model.apply_pose(model.animations['Wind'][0])
    msgs=[]
    editor=SimpleNamespace(model=model,anim=SimpleNamespace(currentText=lambda:'Wind'),frame=0,
          _active_project_id='testing',_pose_live_id=model.pose_id('Wind',0),
          _pose_draft_key=('testing','Wind',0,model.pose_id('Wind',0)),
          _pose_draft_dirty=False,_next_pose_capture_pending=False,_slimer_pending_part=None,
          _slimer_pending_layer=None,canvas=SimpleNamespace(slimer_transform_mode=False),
          slimer_selection=None,status=SimpleNamespace(setText=msgs.append))
    editor.preserve_pose_draft=lambda:suite_method('preserve_pose_draft')(editor)
    editor._prepare_artwork_export=lambda:suite_method('_prepare_artwork_export')(editor)
    return editor,msgs


def test_all_alpha_values_remain_visible_even_for_disconnected_single_pixels(tmp_path):
    frames=[]
    for shift in (0,1,2):
        img=Image.new('RGBA',(32,16))
        img.putpixel((2+shift,2),(200,10,20,255))
        img.putpixel((30-shift,14),(23,180,244,40))
        img.putpixel((5+shift,7),(110,70,30,1))
        img.putpixel((7,8),(100,255,220,125))
        frames.append(img)
    before=[i.tobytes() for i in frames]
    out=tmp_path/'wind.gif'
    encode_gif(frames,[90,110,130],out)
    with Image.open(out) as gif:
        assert gif.n_frames==3
        for index,expected in enumerate(frames):
            gif.seek(index)
            actual=gif.convert('RGBA')
            for y in range(16):
                for x in range(32):
                    assert (actual.getpixel((x,y))[3]>0)==(expected.getpixel((x,y))[3]>0), (index,x,y)
    assert [i.tobytes() for i in frames]==before
    apng=tmp_path/'wind.png'
    encode_apng(frames,[90,110,130],apng)
    with Image.open(apng) as result:
        for i,expected in enumerate(frames):
            result.seek(i)
            assert result.convert('RGBA').tobytes()==expected.tobytes()


def test_cleaner_stroke_is_written_to_saved_pose_before_any_export():
    editor,msgs=make_editor()
    old=editor.model.render(editor.model.animations['Wind'][0])
    assert old.getpixel((1,1))[3]==255
    modified=set()
    assert erase_visible_pixels(editor.model.parts,1,1,states=editor.model.resolved_pose(),
        canvas_size=editor.model.size,modified_indices=modified)
    for part in modified:
        editor.model.originals[part]=editor.model.parts[part]['image'].copy()
    editor._pose_draft_dirty=True
    # No frame switching, manual Save Pose, or additional user action required.
    assert editor._prepare_artwork_export()
    updated=editor.model.render(editor.model.animations['Wind'][0])
    assert updated.getpixel((1,1))[3]==0
    assert updated.getpixel((15,12))==(75,188,255,40)
    assert not editor._pose_draft_dirty
    assert not msgs


def test_export_refuses_unplaced_next_pose_instead_of_silently_using_old_pixels():
    editor,msgs=make_editor()
    editor._next_pose_capture_pending=True
    editor.model.originals[0].putpixel((1,1),(0,0,0,0))
    assert not editor._prepare_artwork_export()
    assert editor.model.render(editor.model.animations['Wind'][0]).getpixel((1,1))[3]==255
    assert any('Place Frame' in m for m in msgs)


def test_export_refuses_dirty_pose_when_ownership_unverifiable():
    editor,msgs=make_editor()
    editor._pose_draft_key=('wrong','Wind',0,'wrong')
    editor._pose_draft_dirty=True
    assert not editor._prepare_artwork_export()
    assert any('Export blocked' in m for m in msgs)


def test_every_png_gif_sheet_export_path_runs_preflight():
    code=WIZARD.read_text(encoding='utf-8')
    tree=ast.parse(code)
    suite=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Suite')
    for name in ('export_current_frame','export_all_frames','export_animated','export'):
        m=next(n for n in suite.body if isinstance(n,ast.FunctionDef) and n.name==name)
        assert any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)
                   and n.func.attr=='_prepare_artwork_export' for n in ast.walk(m)),name
