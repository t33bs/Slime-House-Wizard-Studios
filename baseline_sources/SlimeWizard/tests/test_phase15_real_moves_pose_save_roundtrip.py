"""Full production Slimer moves -> independent poses -> disk -> pose navigation."""
from PIL import Image
from studio.pet_suite_model import PetSuiteModel
from test_phase15_real_edit_apply_consecutive import Harness, Selection


def _move(h, source, destination):
    mask = Image.new('L', h.model.size)
    mask.putpixel(source, 255)
    h.slimer_selection = Selection(h.model.render(), mask)
    assert h.slimer_create_editable_layer(), h.status.value
    h._slimer_pending_part['x'] = destination[0] - source[0]
    h._slimer_pending_part['y'] = destination[1] - source[1]
    assert h.slimer_apply_move_to_pose(), h.status.value
    assert h._slimer_pending_part is None


def test_three_real_moves_survive_pose_navigation_and_disk(tmp_path):
    h = Harness()
    original = Image.new('RGBA', (16, 16))
    red, green = (241, 30, 50, 255), (25, 219, 65, 255)
    original.putpixel((2, 2), red)
    original.putpixel((5, 5), green)
    h.model.import_part('Base', original)
    animation = h.model.current
    # First pose is created before Slimer adds new editable assets.
    pose_one = h.model.snapshot()
    h.model.animations[animation] = [pose_one]

    _move(h, (2, 2), (8, 8))
    _move(h, (5, 5), (11, 11))
    _move(h, (8, 8), (13, 13))  # select a previous Slimer layer
    pose_two = h.model.snapshot()
    h.model.animations[animation].append(pose_two)
    rendered_two = h.model.render().tobytes()
    assert len(pose_two) == 4
    assert h.model.render().getpixel((13, 13)) == red
    assert h.model.render().getpixel((11, 11)) == green

    # Edit a layer only in a third pose; do not rewrite pose two.
    h.model.parts[3]['x'] += 1
    pose_three = h.model.snapshot()
    h.model.animations[animation].append(pose_three)
    rendered_three = h.model.render().tobytes()
    assert rendered_three != rendered_two

    project = tmp_path / 'three_moves.rig.json'
    h.model.save_project(project)
    restored = PetSuiteModel.load_project(project)
    assert len(restored.parts) == 4
    assert len(restored.animations[animation]) == 3
    for index, expected in [(0, original.tobytes()), (1, rendered_two),
                            (2, rendered_three), (1, rendered_two),
                            (0, original.tobytes()), (2, rendered_three)]:
        pose = restored.animations[animation][index]
        restored.apply_pose(pose)
        assert restored.render().tobytes() == expected
        assert restored.snapshot()[:len(pose)] == pose


def test_copy_mode_layers_survive_saved_poses_and_reopen(tmp_path):
    h = Harness()
    h.slimer_move_original.setChecked(False)
    original = Image.new('RGBA', (16, 16))
    color = (30, 110, 245, 255)
    original.putpixel((2, 2), color)
    h.model.import_part('Base', original)
    animation = h.model.current
    h.model.animations[animation] = [h.model.snapshot()]
    _move(h, (2, 2), (7, 7))
    _move(h, (2, 2), (12, 12))
    copied = h.model.snapshot()
    h.model.animations[animation].append(copied)
    path = tmp_path / 'copies.rig.json'
    h.model.save_project(path)
    restored = PetSuiteModel.load_project(path)
    restored.apply_pose(restored.animations[animation][0])
    assert restored.render().getpixel((2, 2)) == color
    assert restored.render().getpixel((7, 7))[3] == 0
    restored.apply_pose(restored.animations[animation][1])
    for xy in ((2, 2), (7, 7), (12, 12)):
        assert restored.render().getpixel(xy) == color
    assert len(restored.parts) == 3
