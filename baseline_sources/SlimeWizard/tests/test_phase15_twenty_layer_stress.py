"""Stress model persistence with twenty independently transformed Slimer assets."""
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


def test_twenty_independent_layers_survive_pose_switch_and_reload(tmp_path):
    model = PetSuiteModel((128, 128))
    original = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
    original.putpixel((1, 1), (255, 255, 255, 255))
    model.import_part('Original', original)
    animation = model.current
    old_pose = model.snapshot()
    model.animations[animation] = [old_pose]
    for number in range(1, 21):
        asset = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
        asset.putpixel((3, 3), (number * 10, 255 - number * 10, number * 7, 255))
        model.import_part(f'Slimer Layer {number:03d}', asset)
        model.parts[-1]['x'] = number
        model.parts[-1]['y'] = number + 2
    first_pose = model.snapshot()
    model.animations[animation].append(first_pose)
    for number in range(1, 21):
        part = model.parts[number]
        part['x'] = number + 10
        part['y'] = number + 12
        model.resize_part(number, 16 + number, 16 + number)
        model.rotate_part(number, 90 if number % 2 else 180)
    second_pose = model.snapshot()
    model.animations[animation].append(second_pose)
    path = tmp_path / 'twenty_layers.rig.json'
    model.save_project(path)
    loaded = PetSuiteModel.load_project(path)
    for pose_index in (0, 1, 2, 1, 0, 2, 1):
        expected = loaded.animations[animation][pose_index]
        loaded.apply_pose(expected)
        assert loaded.snapshot() == expected if pose_index != 0 else loaded.snapshot()[:1] == expected
        assert len(loaded.parts) == 21
        for number in range(1, 21):
            assert loaded.parts[number]['name'] == f'Slimer Layer {number:03d}'
            assert loaded.parts[number]['visible'] is (pose_index != 0)
            if pose_index == 1:
                assert loaded.parts[number]['x'] == number
            if pose_index == 2:
                assert loaded.parts[number]['x'] == number + 10
                assert loaded.snapshot()[number]['angle'] == (90 if number % 2 else 180)
        loaded.render()
