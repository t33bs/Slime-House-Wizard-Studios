"""Phase 92: placing later poses must not flatten earlier edited pose layers.

A saved pose retains its individual source/Slimer layers for repeat editing.
Only the next pose gets one composite base.  Move Original removes source
pixels at their OLD coordinates, not from the moved destination.
"""
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


def test_edited_first_pose_keeps_source_layers_when_next_pose_is_merged(tmp_path):
    model = PetSuiteModel((128, 128))
    original = Image.new('RGBA', (128, 128))
    original.putpixel((20, 30), (220, 80, 50, 255))
    original.putpixel((50, 60), (40, 200, 130, 138))
    model.import_part('Source', original)
    moved_opaque = Image.new('RGBA', (128, 128))
    moved_opaque.putpixel((24, 30), (220, 80, 50, 255))
    model.originals[0].putpixel((20,30), (0,0,0,0))
    model.resize_part(0,128,128)
    model.import_part('Slimer Layer 001', moved_opaque)

    # The FIRST placed pose is one combined editable source.
    first = model.merged_working_pose(model.snapshot(), 'Combined Artwork 003')
    model.insert_frame('Idle / Breathing', 0, first)
    model.apply_pose(first)
    assert [i for i,s in enumerate(first) if s['visible']] == [2]
    assert model.render(first).getpixel((50,60))[3] == 138

    # A subsequent Move Original in Pose 1 creates an independently editable
    # second layer and must erase only the old coordinate in Pose 1's base.
    combined_source = model.originals[2].copy()
    combined_source.putpixel((50,60), (0,0,0,0))
    model.originals[2] = combined_source
    model.resize_part(2,128,128)
    moved_translucent = Image.new('RGBA', (128, 128))
    moved_translucent.putpixel((53,60), (40,200,130,138))
    model.import_part('Slimer Layer 002', moved_translucent)
    model.save_pose_at('Idle / Breathing', 0)
    pose_one = model.animations['Idle / Breathing'][0]
    assert [i for i,s in enumerate(pose_one) if s['visible']] == [2,3]
    assert model.render(pose_one).getpixel((50,60))[3] == 0
    assert model.render(pose_one).getpixel((53,60))[3] == 138
    # Place Pose 2. Only Pose 2 may receive the flattened editable working
    # base; the previously saved Pose 1 must remain layered.
    second = model.merged_working_pose(model.snapshot(), 'Combined Artwork 005')
    model.insert_frame('Idle / Breathing', 1, second)
    assert [i for i,s in enumerate(second) if s['visible']] == [4]
    assert [i for i,s in enumerate(pose_one) if s['visible']] == [2,3]
    assert model.render(second).tobytes() == model.render(pose_one).tobytes()

    # Both poses survive file persistence and a roundtrip through the editor.
    path = tmp_path / 'poses.swp'
    model.save_project(path)
    reopened = PetSuiteModel.load_project(path)
    saved = reopened.animations['Idle / Breathing']
    assert [i for i,s in enumerate(saved[0]) if s['visible']] == [2,3]
    assert [i for i,s in enumerate(saved[1]) if s['visible']] == [4]
    reopened.apply_pose(saved[0])
    assert reopened.render().getpixel((53,60))[3] == 138
    reopened.apply_pose(saved[1])
    assert reopened.render().getpixel((53,60))[3] == 138
