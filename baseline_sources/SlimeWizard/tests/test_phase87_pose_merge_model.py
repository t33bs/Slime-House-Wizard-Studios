"""Phase 87: merged NEW pose, independently editable earlier poses."""
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


def sprite(dots):
    image=Image.new('RGBA',(128,128))
    for pos,rgba in dots.items():
        image.putpixel(pos,rgba)
    return image


def test_merge_new_pose_preserves_prior_rgba_and_prior_editable_sources():
    model=PetSuiteModel((128,128))
    body=sprite({(20,30):(190,80,30,255),(21,30):(50,90,200,144)})
    arm=sprite({(30,30):(70,220,70,255)})
    model.import_part('Swordcat Body',body)
    model.import_part('Slimer Layer 001',arm)
    source=model.snapshot()
    original=model.render(source)
    model.insert_frame('Idle / Breathing',0,source)
    merged=model.merged_working_pose(source,'Combined Artwork 003')
    new_index=model.insert_frame('Idle / Breathing',1,merged)
    assert new_index==1
    assert len(model.animations['Idle / Breathing'][0])==2
    assert [p['visible'] for p in merged]==[False,False,True]
    assert model.render(merged).tobytes()==original.tobytes()
    assert model.animations['Idle / Breathing'][0]==source
    # Each source is still separately recorded in its original pose.
    assert model._decode_source(source[0]['source_png']).tobytes()==body.tobytes()
    assert model._decode_source(source[1]['source_png']).tobytes()==arm.tobytes()
    # A new Slimer cut in Pose 2 must never rewrite Pose 1.
    model.apply_pose(merged)
    model.originals[-1].putpixel((21,30),(0,0,0,0))
    model.resize_part(2,128,128)
    edited=model.snapshot()
    assert model.render(edited).getpixel((21,30))[3]==0
    assert model.render(source).tobytes()==original.tobytes()


def test_second_and_third_new_poses_remerge_from_latest_visible_art_only():
    model=PetSuiteModel((128,128))
    body=sprite({(20,30):(190,80,30,255)})
    model.import_part('Swordcat Body',body)
    model.import_part('Slimer Layer 001',sprite({(21,31):(12,50,200,112)}))
    first=model.snapshot()
    model.insert_frame('Idle / Breathing',0,first)
    second=model.merged_working_pose(first,'Combined Artwork 003')
    model.insert_frame('Idle / Breathing',1,second)
    model.apply_pose(second)
    model.import_part('Slimer Layer 002',sprite({(32,32):(90,200,100,220)}))
    second_edited=model.snapshot()
    model.save_pose_at('Idle / Breathing',1)
    before=model.render(second_edited)
    third=model.merged_working_pose(second_edited,'Combined Artwork 005')
    model.insert_frame('Idle / Breathing',2,third)
    assert model.render(third).tobytes()==before.tobytes()
    assert [state['visible'] for state in third]==[False,False,False,False,True]
    assert len(model.animations['Idle / Breathing'][0])==2
    assert model.render(first).getpixel((32,32))[3]==0
    assert model.render(third).getpixel((32,32))==(90,200,100,220)


def test_merged_pose_saved_and_reloaded(tmp_path):
    model=PetSuiteModel((128,128))
    model.import_part('Swordcat',sprite({(50,51):(180,190,100,255)}))
    model.import_part('Slimer Layer 001',sprite({(71,72):(100,80,200,132)}))
    first=model.snapshot()
    model.insert_frame('Idle / Breathing',0,first)
    second=model.merged_working_pose(first,'Combined Artwork 003')
    model.insert_frame('Idle / Breathing',1,second)
    path=tmp_path/'sw87.json'
    model.save_project(path)
    loaded=PetSuiteModel.load_project(path)
    poses=loaded.animations['Idle / Breathing']
    assert len(poses)==2
    assert len(poses[0])==2 and len(poses[1])==3
    assert loaded.render(poses[0]).tobytes()==loaded.render(poses[1]).tobytes()
    loaded.apply_pose(poses[0]); assert loaded.parts[0]['visible']
    loaded.apply_pose(poses[1]); assert not loaded.parts[0]['visible']
    assert loaded.parts[2]['visible']


def test_merge_preserves_visible_overlap_composite_and_undo():
    from studio.edit_history import EditHistory
    model=PetSuiteModel((128,128))
    bottom=sprite({(31,32):(20,120,210,255)})
    top=sprite({(31,32):(220,50,40,144)})
    model.import_part('Swordcat',bottom)
    model.import_part('Slimer Layer 001',top)
    model.insert_frame('Idle / Breathing',0)
    previous=model.animations['Idle / Breathing'][0]
    expected=model.render(previous).tobytes()
    history=EditHistory()
    history.record(model)
    merged=model.merged_working_pose(previous,'Combined Artwork 001')
    model.insert_frame('Idle / Breathing',1,merged)
    assert model.render(merged).tobytes()==expected
    assert history.undo(model)
    assert len(model.parts)==2
    assert len(model.animations['Idle / Breathing'])==1
    assert model.render(previous).tobytes()==expected
    assert history.redo(model)
    assert len(model.parts)==3
    assert len(model.animations['Idle / Breathing'])==2
    assert model.render(model.animations['Idle / Breathing'][1]).tobytes()==expected
