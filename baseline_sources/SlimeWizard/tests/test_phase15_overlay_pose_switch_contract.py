"""Headless saved-pose isolation checks for repeatable Slimer overlay edits."""
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


def test_overlay_edits_survive_pose_switch_without_leaking_to_earlier_frame():
    model = PetSuiteModel((24, 24))
    base = Image.new('RGBA', (24, 24))
    base.putpixel((2, 2), (210, 30, 70, 123))
    model.import_part('Creature', base)
    model.import_part('Slimer pose overlay', Image.new('RGBA', model.size))
    first = model.snapshot()
    model.animations['Idle'] = [first]

    # The second pose has two successive working-pose overlay edits.
    edited_base = model.originals[0].copy()
    edited_base.putpixel((2, 2), (0, 0, 0, 0))
    model.originals[0] = edited_base
    model.parts[0]['image'] = edited_base.copy()
    overlay = model.originals[1].copy()
    overlay.putpixel((4, 2), (210, 30, 70, 123))
    overlay.putpixel((7, 7), (15, 120, 230, 199))
    model.originals[1] = overlay
    model.parts[1]['image'] = overlay.copy()
    second = model.snapshot()
    model.animations['Idle'].append(second)

    for _ in range(3):
        model.apply_pose(first)
        assert model.render().getpixel((2, 2)) == (210, 30, 70, 123)
        assert model.render().getpixel((4, 2))[3] == 0
        assert model.render().getpixel((7, 7))[3] == 0
        model.apply_pose(second)
        assert model.render().getpixel((2, 2))[3] == 0
        assert model.render().getpixel((4, 2)) == (210, 30, 70, 123)
        assert model.render().getpixel((7, 7)) == (15, 120, 230, 199)
    assert len(model.animations['Idle']) == 2
