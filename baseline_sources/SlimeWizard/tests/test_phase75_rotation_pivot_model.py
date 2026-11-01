"""Non-GUI guard for rotating a tiny selected region in a full-canvas layer."""
from PIL import Image
from studio.pet_suite_model import PetSuiteModel
from studio.slimer_destination import destination_fits_canvas


def test_full_canvas_slimer_layer_rotates_about_actual_artwork():
    model = PetSuiteModel()
    image = Image.new('RGBA', (128, 128))
    image.putpixel((40, 50), (255, 0, 0, 255))
    image.putpixel((40, 51), (0, 255, 0, 255))
    image.putpixel((41, 51), (0, 0, 255, 255))
    model.import_part('selected artwork', image)
    i = len(model.parts) - 1
    l, t, r, b = image.getchannel('A').getbbox()
    model.set_anchor(i, (l + r)//2, (t + b)//2)
    model.rotate_part(i, 90)
    result = model.render()
    assert result.getpixel((40, 50))[3] == 0
    assert result.getpixel((41, 50)) == (0, 0, 255, 255)
    assert result.getpixel((40, 51)) == (255, 0, 0, 255)
    assert destination_fits_canvas(image, 0, 0, 90, model.anchors[i], model.size)
    assert result.getpixel((80, 80))[3] == 0


def test_rotation_at_canvas_edge_is_still_rejected():
    image = Image.new('RGBA', (128, 128))
    image.putpixel((0, 0), (255, 0, 0, 255))
    image.putpixel((1, 0), (0, 255, 0, 255))
    assert not destination_fits_canvas(image, 0, 0, 90, [1, 0], (128, 128))
