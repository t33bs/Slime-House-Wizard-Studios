"""Stress timeline snapshots with repeated semi-transparent pose edits and recovery."""
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


def test_repeated_pose_edits_do_not_degrade_neighbor_pixels():
    model = PetSuiteModel((32, 32))
    sprite = Image.new('RGBA', (6, 6), (17, 110, 230, 127))
    sprite.putpixel((2, 2), (250, 20, 40, 255))
    model.import_part('swordcat foot', sprite)
    for x in (2, 10, 18):
        model.parts[0]['x'] = x
        model.insert_frame('Walk', len(model.animations.get('Walk', [])))
    first = model.render(model.animations['Walk'][0]).tobytes()
    third = model.render(model.animations['Walk'][2]).tobytes()
    for i in range(100):
        model.edit_pose_at('Walk', 1, {0: {'x': 11 if i % 2 else 12}})
        assert model.render(model.animations['Walk'][0]).tobytes() == first
        assert model.render(model.animations['Walk'][2]).tobytes() == third
    assert model.restore_previous_pose('Walk', 1)
    assert model.render(model.animations['Walk'][0]).tobytes() == first
    assert model.render(model.animations['Walk'][2]).tobytes() == third


def test_pose_repeated_render_is_byte_identical():
    model = PetSuiteModel((16, 16))
    model.import_part('translucent pixel', Image.new('RGBA', (5, 5), (80, 90, 120, 80)))
    model.insert_frame('Idle', 0)
    expected = model.render(model.animations['Idle'][0]).tobytes()
    for _ in range(200):
        assert model.render(model.animations['Idle'][0]).tobytes() == expected
