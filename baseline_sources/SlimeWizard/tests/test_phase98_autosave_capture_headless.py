"""Headless regression: an autosave tick never commits a next-pose draft."""
import ast
from pathlib import Path
from types import SimpleNamespace
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


def _extract_method(name):
    path=Path(__file__).resolve().parents[1]/'friendly_animator.py'
    tree=ast.parse(path.read_text())
    suite=next(node for node in tree.body if isinstance(node,ast.ClassDef) and node.name=='Suite')
    method=next(node for node in suite.body if isinstance(node,ast.FunctionDef) and node.name==name)
    mod=ast.Module(body=[method],type_ignores=[])
    ast.fix_missing_locations(mod)
    scope={}
    exec(compile(mod,str(path),'exec'),scope)
    return scope[name]


def test_two_leg_edit_draft_survives_recovery_without_replacing_pose1():
    model=PetSuiteModel()
    img=Image.new('RGBA',(128,128))
    img.putpixel((20,60),(220,30,30,255))
    img.putpixel((40,60),(30,80,220,255))
    model.import_part('Swordcat',img)
    animation=model.current
    model.insert_frame(animation,0,model.snapshot())
    pid=model.pose_id(animation,0)
    preserved=model.render(model.animations[animation][0]).tobytes()
    # Mimic two Apply Move commits to the live source without new Place Frame.
    altered=model.originals[0].copy()
    altered.putpixel((20,60),(0,0,0,0))
    altered.putpixel((23,60),(220,30,30,255))
    altered.putpixel((40,60),(0,0,0,0))
    altered.putpixel((44,60),(30,80,220,255))
    model.originals[0]=altered
    model.parts[0]['image']=altered.copy()
    target=SimpleNamespace(
        model=model, _next_pose_capture_pending=True,
        _pose_draft_key=(42,animation,0,pid), _active_project_id=42,
        _pose_live_id=pid, _pose_draft_dirty=True)
    preserve=_extract_method('preserve_pose_draft')
    preserve(target)  # as called by the minute timer
    assert model.render(model.animations[animation][0]).tobytes()==preserved
    assert model.render().tobytes()!=preserved
    # An explicit save is distinct: the guard is lifted by Save Current Pose.
    target._next_pose_capture_pending=False
    target._slimer_pending_layer=None
    target.slimer_selection=None
    target.canvas=SimpleNamespace(slimer_transform_mode=False)
    target.status=SimpleNamespace(setText=lambda *a:None)
    preserve(target)
    assert model.render(model.animations[animation][0]).tobytes()!=preserved
