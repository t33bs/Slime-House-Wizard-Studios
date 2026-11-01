"""Headless contracts backing the beginner's 'move twice, Place Frame' sequence."""
from pathlib import Path
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


def test_model_records_changed_canvas_as_next_without_rewriting_saved_original(tmp_path):
    model = PetSuiteModel((128,128))
    base = Image.new('RGBA',(128,128))
    base.putpixel((20,80),(200,40,50,255))
    base.putpixel((60,80),(30,170,250,255))
    model.import_part('Swordcat',base)
    name = model.current
    model.insert_frame(name,0,model.snapshot())
    original = model.render(model.animations[name][0]).tobytes()
    original_id = model.pose_id(name,0)

    # Simulate two independent Slimer Move Original edits on the live canvas.
    new_base = base.copy()
    new_base.putpixel((20,80),(0,0,0,0))
    new_base.putpixel((60,80),(0,0,0,0))
    model.originals[0]=new_base
    model.parts[0]['image']=new_base.copy()
    right = Image.new('RGBA',(128,128))
    right.putpixel((24,80),(200,40,50,255))
    model.import_part('Slimer Layer 001',right)
    left = Image.new('RGBA',(128,128))
    left.putpixel((55,80),(30,170,250,255))
    model.import_part('Slimer Layer 002',left)
    working=model.snapshot()
    combined=model.merged_working_pose(working,'Combined Artwork 004')
    model.insert_frame(name,1,combined)

    assert model.pose_id(name,0)==original_id
    assert model.render(model.animations[name][0]).tobytes()==original
    assert model.render(model.animations[name][1]).tobytes()!=original
    assert model.render(model.animations[name][1]).getpixel((24,80))==(200,40,50,255)
    assert model.render(model.animations[name][1]).getpixel((55,80))==(30,170,250,255)
    assert [i for i,s in enumerate(model.animations[name][0]) if s['visible']]==[0]
    assert [i for i,s in enumerate(model.animations[name][1]) if s['visible']]==[3]
    # Sprite-sheet output must also contain two distinct poses, not two
    # duplicates from the live canvas.
    sheet_path=model.export(tmp_path,'walk',columns=2)
    with Image.open(sheet_path) as sheet:
        first=sheet.crop((0,0,128,128)).convert('RGBA')
        second=sheet.crop((128,0,256,128)).convert('RGBA')
        assert first.tobytes()==original
        assert second.tobytes()==model.render(model.animations[name][1]).tobytes()
        assert first.tobytes()!=second.tobytes()


def test_place_frame_source_does_not_autosave_edited_live_canvas_to_prior_pose():
    source=Path(__file__).resolve().parents[1].joinpath('friendly_animator.py').read_text()
    body=source.split('    def slimer_place_frame(self):',1)[1].split('    def remember(self):',1)[0]
    assert '\n        self.preserve_pose_draft()' not in body
    assert 'old_frames = deepcopy(self.model.animations.get(name, []))' in body
    assert 'source_pose = self.model.snapshot()' in body
    assert 'self.model.insert_frame(name, self.frame + 1, source_pose)' in body
    assert '_insert_next_working_pose(name, self.frame + 1, source_pose)' in body
