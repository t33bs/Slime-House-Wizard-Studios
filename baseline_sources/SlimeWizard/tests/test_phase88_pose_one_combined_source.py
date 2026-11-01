"""Phase 88: the *first* placed Slimer-built pose also gets one editable base.

Model-level checks preserve pixels, hidden original layers, and old saved poses.
"""
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


def _sprite():
    image = Image.new('RGBA', (128, 128))
    image.putpixel((20, 40), (220, 120, 50, 255))
    image.putpixel((21, 40), (220, 120, 50, 135))
    image.putpixel((55, 60), (60, 180, 80, 255))
    return image


def test_first_merged_working_pose_preserves_original_layers_as_hidden_snapshots():
    model = PetSuiteModel()
    model.import_part('Swordcat Source', _sprite())
    edit = Image.new('RGBA', (128, 128))
    edit.putpixel((28, 40), (220, 120, 50, 255))
    model.import_part('Slimer Layer 001', edit)
    model.originals[0].putpixel((20, 40), (0, 0, 0, 0))
    model.parts[0]['image'].putpixel((20, 40), (0, 0, 0, 0))
    original = model.snapshot()
    before = model.render(original).tobytes()

    first = model.merged_working_pose(original, 'Combined Artwork 003')
    model.insert_frame('Idle / Breathing', 0, first)
    model.apply_pose(first)
    assert len(model.animations['Idle / Breathing']) == 1
    assert [p['visible'] for p in first] == [False, False, True]
    assert first[0]['source_png'] == original[0]['source_png']
    assert first[1]['source_png'] == original[1]['source_png']
    assert model.render(first).tobytes() == before
    assert model.render().tobytes() == before
    # A later pose starts with the exact visible pixels after editing pose one.
    subsequent = model.merged_working_pose(model.snapshot(), 'Combined Artwork 004')
    model.insert_frame('Idle / Breathing', 1, subsequent)
    assert [i for i, p in enumerate(subsequent) if p['visible']] == [3]
    assert model.render(subsequent).tobytes() == before
    assert [i for i,p in enumerate(model.animations['Idle / Breathing'][0]) if p['visible']] == [2]


def test_plain_rig_does_not_require_combined_layer():
    model = PetSuiteModel()
    model.import_part('Body', _sprite())
    model.import_part('Head', _sprite())
    model.insert_frame('Idle / Breathing', 0)
    assert len(model.parts) == 2
    assert all(p['visible'] for p in model.animations['Idle / Breathing'][0])


def test_first_combined_pose_survives_project_save_reopen(tmp_path):
    model = PetSuiteModel()
    model.import_part('Original Swordcat', _sprite())
    slimer = Image.new('RGBA', (128, 128))
    slimer.putpixel((25, 40), (220, 120, 50, 255))
    model.import_part('Slimer Layer 001', slimer)
    raw = model.snapshot()
    first = model.merged_working_pose(raw, 'Combined Artwork 003')
    model.insert_frame('Idle / Breathing', 0, first)
    model.apply_pose(first)
    before = model.render(first).tobytes()
    project = tmp_path / 'first_combined.swp'
    model.save_project(project)
    restored = PetSuiteModel.load_project(project)
    pose = restored.animations['Idle / Breathing'][0]
    assert [i for i, part in enumerate(pose) if part['visible']] == [2]
    assert pose[0]['source_png'] == raw[0]['source_png']
    assert pose[1]['source_png'] == raw[1]['source_png']
    assert restored.render(pose).tobytes() == before
