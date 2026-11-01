"""Headless regression for repeatable, independent pixel edits in the working pose."""
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


def test_working_pose_moves_multiple_regions_without_touching_saved_frame():
    model = PetSuiteModel((32, 32))
    source = Image.new('RGBA', (32, 32))
    arm = (240, 40, 70, 125)
    leg = (20, 190, 90, 210)
    source.putpixel((3, 3), arm)
    source.putpixel((12, 12), leg)
    model.import_part('Creature', source)
    saved = model.snapshot()
    model.animations['Idle'] = [saved]
    overlay = Image.new('RGBA', model.size)
    model.import_part('Slimer pose overlay', overlay)

    def move(src, dst):
        # Model-level equivalent of a safe Move Original commit: source is
        # cleared, destination receives the exact RGBA, no frame inserted.
        pixel = model.render().getpixel(src)
        assert pixel[3] > 0
        index = 1 if model.originals[1].getpixel(src)[3] else 0
        layer = model.originals[index].copy()
        layer.putpixel(src, (0, 0, 0, 0))
        model.originals[index] = layer
        model.parts[index]['image'] = layer.copy()
        placed = model.originals[1].copy()
        placed.putpixel(dst, pixel)
        model.originals[1] = placed
        model.parts[1]['image'] = placed.copy()
        assert model.render().getpixel(src)[3] == 0
        assert model.render().getpixel(dst) == pixel
        assert len(model.animations['Idle']) == 1

    move((3, 3), (5, 3))
    move((12, 12), (14, 12))
    move((5, 3), (7, 3))
    assert model.render().getpixel((7, 3)) == arm
    assert model.render().getpixel((14, 12)) == leg
    assert model.render(saved).getpixel((3, 3)) == arm
    assert model.render(saved).getpixel((12, 12)) == leg
    assert model.render(saved).getpixel((7, 3))[3] == 0
