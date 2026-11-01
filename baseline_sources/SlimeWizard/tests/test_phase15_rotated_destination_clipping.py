from PIL import Image
from studio.slimer_destination import destination_fits_canvas


def test_rotated_partially_clipped_rejected():
    im = Image.new('RGBA', (20, 20))
    im.putpixel((0, 0), (255, 0, 0, 255))
    im.putpixel((19, 19), (0, 255, 0, 255))
    assert not destination_fits_canvas(im, -1, 20, 45, (10, 10), (128, 128))
    assert destination_fits_canvas(im, 40, 40, 45, (10, 10), (128, 128))


def test_unrotated_edge_and_empty():
    im = Image.new('RGBA', (20, 20))
    im.putpixel((0, 0), (255, 0, 0, 255))
    assert destination_fits_canvas(im, 0, 0, 0, (10, 10), (128, 128))
    assert not destination_fits_canvas(im, -1, 0, 0, (10, 10), (128, 128))
    assert not destination_fits_canvas(Image.new('RGBA', (20, 20)), 0, 0, 0, (10, 10), (128, 128))


def test_rotated_pre_rotation_clipping_rejected_even_if_rotation_would_fit():
    # A pixel outside the canvas before rotation is discarded by render_part.
    # The rotated destination itself can be entirely inside, which must not
    # allow Move Original to erase the pixel from its source.
    im = Image.new('RGBA', (20, 20))
    im.putpixel((0, 10), (255, 0, 0, 255))
    assert not destination_fits_canvas(im, -1, 20, 90, (10, 10), (128, 128))
    assert destination_fits_canvas(im, 0, 20, 90, (10, 10), (128, 128))


def test_rotated_pre_rotation_clipping_right_bottom_rejected():
    im = Image.new('RGBA', (20, 20))
    im.putpixel((19, 19), (255, 0, 0, 255))
    assert not destination_fits_canvas(im, 110, 110, 180, (10, 10), (128, 128))
