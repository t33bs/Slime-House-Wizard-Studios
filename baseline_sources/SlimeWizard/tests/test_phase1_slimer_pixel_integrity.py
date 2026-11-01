"""Phase 1 regression checks: exact pixel movement and immutable saved poses."""
from PIL import Image
from studio.slimer_tool import SlimerSelection
from studio.pet_suite_model import PetSuiteModel


def test_slimer_transform_preserves_semitransparent_alpha():
    source = Image.new('RGBA', (8, 8), (0, 0, 0, 0))
    source.putpixel((2, 2), (240, 10, 30, 128))
    selection = SlimerSelection.empty(source)
    selection.paint(2, 2)
    moved = selection.transform(dx=2)
    assert moved.getpixel((4, 2)) == (240, 10, 30, 128)
    assert moved.getpixel((2, 2))[3] == 0


def test_slimer_compose_move_original_does_not_mutate_source():
    source = Image.new('RGBA', (8, 8), (0, 0, 0, 0))
    source.putpixel((2, 2), (255, 0, 0, 255))
    selection = SlimerSelection.empty(source)
    selection.paint(2, 2)
    preview = selection.transform(dx=2)
    moved = selection.compose(preview, move_original=True)
    assert moved.getpixel((2, 2))[3] == 0
    assert moved.getpixel((4, 2)) == (255, 0, 0, 255)
    assert source.getpixel((2, 2)) == (255, 0, 0, 255)


def test_saved_poses_keep_independent_source_pixels():
    model = PetSuiteModel((8, 8))
    original = Image.new('RGBA', (8, 8), (0, 0, 0, 0))
    original.putpixel((1, 1), (255, 0, 0, 255))
    model.import_part('leg', original)
    model.insert_frame('Idle', 0)
    model.parts[0]['x'] = 2
    model.insert_frame('Idle', 1)
    model.parts[0]['x'] = 4
    model.insert_frame('Idle', 2)
    poses = model.animations['Idle']
    assert [p[0]['x'] for p in poses] == [0, 2, 4]
    model.parts[0]['x'] = 6
    assert [p[0]['x'] for p in poses] == [0, 2, 4]
