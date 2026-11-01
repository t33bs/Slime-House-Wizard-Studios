from PIL import Image
from studio.pet_suite_model import PetSuiteModel


def test_imported_png_pose_is_independent_of_neighbors():
    model = PetSuiteModel(size=(8, 8))
    base = Image.new('RGBA', (8, 8), (100, 30, 10, 255))
    model.import_part('Base', base)
    animation = 'Idle / Breathing'
    model.insert_frame(animation, 0)
    model.insert_frame(animation, 1)
    before = [model.render(p).tobytes() for p in model.animations[animation]]
    image = Image.new('RGBA', (8, 8), (0, 0, 0, 0))
    image.putpixel((2, 3), (50, 80, 120, 90))
    index = model.insert_frame(animation, 1)
    model.replace_frame_image(animation, index, image)
    frames = model.animations[animation]
    assert len(frames) == 3
    assert model.render(frames[0]).tobytes() == before[0]
    assert model.render(frames[2]).tobytes() == before[1]
    assert model.render(frames[1]).getpixel((2, 3)) == (50, 80, 120, 90)
    assert len(set(model.pose_ids[animation])) == 3
