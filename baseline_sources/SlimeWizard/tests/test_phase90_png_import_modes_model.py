"""Phase 90: explicit PNG mode semantics and pose-level RGBA fidelity."""
from copy import deepcopy
from PIL import Image
import pytest
from studio.pet_suite_model import PetSuiteModel


def source():
    model=PetSuiteModel(size=(16,16))
    base=Image.new('RGBA',(16,16))
    base.putpixel((3,3),(0,0,0,255))       # original opaque black
    base.putpixel((4,3),(80,10,10,255))
    base.putpixel((5,3),(21,24,27,100))
    model.import_part('Previous Swordcat',base)
    animation='Idle / Breathing'
    model.insert_frame(animation,0)
    return model,animation


def imported_png():
    png=Image.new('RGBA',(16,16))
    png.putpixel((3,3),(0,0,0,0))          # transparent black is NOT opaque
    png.putpixel((4,3),(0,0,0,255))        # exact opaque black
    png.putpixel((5,3),(0,0,0,128))        # translucent black
    png.putpixel((6,3),(220,100,20,255))
    return png


def test_exact_import_keeps_black_alpha_no_inherited_art_and_pose_isolation():
    model,anim=source()
    old=deepcopy(model.animations[anim][0]); old_pixels=model.render(old).tobytes()
    old_id=model.pose_id(anim,0)
    png=imported_png()
    index=model.insert_frame(anim,1)
    model.replace_frame_image(anim,index,png)
    result=model.render(model.animations[anim][index])
    assert result.tobytes()==png.tobytes()
    assert result.getpixel((3,3))==(0,0,0,0)
    assert result.getpixel((4,3))==(0,0,0,255)
    assert result.getpixel((5,3))==(0,0,0,128)
    assert all(not x['visible'] for x in model.animations[anim][index][:-1])
    assert model.animations[anim][0]==old
    assert model.render(model.animations[anim][0]).tobytes()==old_pixels
    assert model.pose_id(anim,0)==old_id
    assert model.parts[0]['visible']  # *live* old artwork is not modified by imported state


def test_overlay_keeps_base_visible_through_transparency_with_exact_alpha():
    model,anim=source()
    previous=deepcopy(model.animations[anim][0])
    base_pixels=model.render(previous).tobytes()
    png=imported_png()
    expected=model.render(previous).convert('RGBA').copy()
    expected.alpha_composite(png)
    index=model.insert_frame(anim,1)
    model.replace_frame_image(anim,index,png,mode='overlay',base_pose=previous)
    actual=model.render(model.animations[anim][index])
    assert actual.tobytes()==expected.tobytes()
    assert actual.getpixel((3,3))==(0,0,0,255) # base black survives alpha-zero import
    assert actual.getpixel((4,3))==(0,0,0,255)
    assert model.render(model.animations[anim][0]).tobytes()==base_pixels
    assert model.animations[anim][0]==previous
    # PNG source and prior layers remain distinct, immutable snapshots.
    assert model.originals[0].getpixel((5,3))==(21,24,27,100)
    assert model.originals[-1].tobytes()==expected.tobytes()


def test_overlay_from_saved_previous_pose_not_uncommitted_live_asset():
    model,anim=source()
    saved=deepcopy(model.animations[anim][0])
    model.originals[0].putpixel((3,3),(255,0,0,255))
    model.parts[0]['image'].putpixel((3,3),(255,0,0,255))
    index=model.insert_frame(anim,1)
    png=Image.new('RGBA', model.size)
    model.replace_frame_image(anim,index,png,mode='overlay',base_pose=saved)
    assert model.render(model.animations[anim][index]).getpixel((3,3))==(0,0,0,255)


def test_modes_are_guarded_and_size_mismatch_does_not_append_asset():
    model,anim=source()
    index=model.insert_frame(anim,1)
    count=len(model.parts)
    with pytest.raises(ValueError,match='previous pose'):
        model.replace_frame_image(anim,index,imported_png(),mode='overlay')
    with pytest.raises(ValueError,match='mode'):
        model.replace_frame_image(anim,index,imported_png(),mode='blend')
    with pytest.raises(ValueError,match='size'):
        model.replace_frame_image(anim,index,Image.new('RGBA',(8,8)))
    assert len(model.parts)==count


def test_exact_and_overlay_survive_project_save_reload_and_reorder(tmp_path):
    model,anim=source()
    source_pose=deepcopy(model.animations[anim][0])
    i=model.insert_frame(anim,1)
    model.replace_frame_image(anim,i,imported_png(),mode='exact')
    j=model.insert_frame(anim,2)
    model.replace_frame_image(anim,j,imported_png(),mode='overlay',base_pose=source_pose)
    model.set_frame_duration(anim,0,175)
    model.set_frame_duration(anim,1,225)
    model.set_frame_duration(anim,2,275)
    before=[model.render(p).tobytes() for p in model.animations[anim]]
    before_ids=model.pose_ids[anim][:]
    project=tmp_path/'animal.json'
    model.save_project(project)
    restored=PetSuiteModel.load_project(project)
    assert [restored.render(p).tobytes() for p in restored.animations[anim]]==before
    assert restored.pose_ids[anim]==before_ids
    assert [restored.frame_duration(anim,i) for i in range(3)]==[175,225,275]
    restored.reorder_frame(anim,0,2)
    assert [restored.render(p).tobytes() for p in restored.animations[anim]]==[before[1],before[2],before[0]]
