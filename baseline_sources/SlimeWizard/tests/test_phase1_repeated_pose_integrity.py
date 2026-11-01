"""Phase 1 headless regression: pixel fidelity and independent pose snapshots.

These tests do NOT replace Windows Qt mouse-event testing.
"""
from PIL import Image
from studio.pet_suite_model import PetSuiteModel
from studio.slimer_tool import SlimerSelection


def test_repeated_slimer_drag_preserves_original_and_alpha():
    source = Image.new('RGBA', (128, 128))
    source.putpixel((25, 100), (240, 80, 50, 255))
    source.putpixel((26, 100), (70, 90, 220, 128))
    selection = SlimerSelection.empty(source)
    selection.paint(25, 100)
    selection.paint(26, 100)
    original = source.tobytes()
    for i in range(100):
        moved = selection.transform(dx=i % 13, dy=-(i % 7))
        assert selection.source.tobytes() == original
        assert sorted(px[3] for px in moved.get_flattened_data() if px[3]) == [128, 255]


def test_ten_pose_insertions_do_not_modify_earlier_pixels():
    model = PetSuiteModel((128, 128))
    foot = Image.new('RGBA', (128, 128))
    foot.putpixel((25, 100), (255, 30, 30, 255))
    model.import_part('foot', foot)
    snapshots = []
    for index in range(10):
        model.parts[0]['x'] = index
        model.insert_frame('Idle', index)
        snapshots.append(model.render(model.animations['Idle'][index]).tobytes())
        for old in range(index + 1):
            assert model.render(model.animations['Idle'][old]).tobytes() == snapshots[old]


def test_switching_and_saving_one_pose_preserves_other_pose():
    model = PetSuiteModel((128, 128))
    foot = Image.new('RGBA', (128, 128))
    foot.putpixel((25, 100), (255, 30, 30, 255))
    model.import_part('foot', foot)
    for x in (0, 4, 8):
        model.parts[0]['x'] = x
        model.insert_frame('Idle', len(model.animations.get('Idle', [])))
    before = [model.render(p).tobytes() for p in model.animations['Idle']]
    model.apply_pose(model.animations['Idle'][1])
    model.parts[0]['x'] = 6
    model.save_pose_at('Idle', 1)
    assert model.render(model.animations['Idle'][0]).tobytes() == before[0]
    assert model.render(model.animations['Idle'][2]).tobytes() == before[2]
    assert model.render(model.animations['Idle'][1]).tobytes() != before[1]
