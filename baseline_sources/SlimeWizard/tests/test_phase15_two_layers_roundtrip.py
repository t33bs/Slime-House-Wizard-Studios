"""End-to-end model regression for independently editable Slimer-created assets."""
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


def test_two_layer_edits_survive_pose_switch_and_project_roundtrip(tmp_path):
    model = PetSuiteModel((32, 32))
    base = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
    base.putpixel((4, 4), (200, 40, 40, 255))
    model.import_part('Base', base)
    for name, xy, color in (
        ('Slimer Layer 001', (7, 8), (40, 200, 40, 255)),
        ('Slimer Layer 002', (14, 15), (40, 40, 200, 255)),
    ):
        layer = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        layer.putpixel((2, 2), color)
        model.import_part(name, layer)
        model.parts[-1]['x'], model.parts[-1]['y'] = xy
    anim = model.current
    pose_one = model.snapshot()
    model.animations[anim] = [pose_one]
    # Edit both independent assets on pose two, including resize and rotation.
    model.parts[1]['x'], model.parts[1]['y'] = 11, 9
    model.parts[2]['x'], model.parts[2]['y'] = 18, 16
    model.resize_part(1, 16, 16)
    model.rotate_part(2, 90)
    pose_two = model.snapshot()
    model.animations[anim].append(pose_two)
    assert pose_one[1]['x'] == 7 and pose_one[2]['x'] == 14
    assert pose_two[1]['x'] == 11 and pose_two[2]['x'] == 18
    path = tmp_path / 'creature.rig.json'
    model.save_project(path)
    loaded = PetSuiteModel.load_project(path)
    assert loaded.animations[anim] == [pose_one, pose_two]
    for pose in (pose_one, pose_two, pose_one, pose_two):
        loaded.apply_pose(pose)
        assert loaded.snapshot() == pose
        assert loaded.parts[1]['name'] == 'Slimer Layer 001'
        assert loaded.parts[2]['name'] == 'Slimer Layer 002'
    assert pose_two[1]['width'] == 16
    assert pose_two[2]['angle'] == 90


def test_new_slimer_layer_does_not_leak_into_older_pose_after_reload(tmp_path):
    model = PetSuiteModel((16, 16))
    model.import_part('Original', Image.new('RGBA', (16, 16), 'red'))
    anim = model.current
    original_pose = model.snapshot()
    model.animations[anim] = [original_pose]
    model.import_part('Slimer Layer 001', Image.new('RGBA', (16, 16), 'blue'))
    later_pose = model.snapshot()
    model.animations[anim].append(later_pose)
    path = tmp_path / 'poses.rig.json'
    model.save_project(path)
    restored = PetSuiteModel.load_project(path)
    restored.apply_pose(restored.animations[anim][0])
    assert restored.parts[1]['visible'] is False
    assert restored.render().getpixel((0, 0)) == (255, 0, 0, 255)
    restored.apply_pose(restored.animations[anim][1])
    assert restored.parts[1]['visible'] is True
    assert restored.render().getpixel((0, 0)) == (0, 0, 255, 255)
