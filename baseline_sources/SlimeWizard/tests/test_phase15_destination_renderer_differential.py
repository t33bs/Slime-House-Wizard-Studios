"""Exercise destination safety against the actual renderer, including edge positions."""
import random
from PIL import Image
from studio.slimer_destination import destination_fits_canvas


def test_random_safe_rotated_destinations_remain_visible_in_real_renderer():
    rng = random.Random(7101)
    canvas = (48, 48)
    for _ in range(300):
        width, height = rng.randint(1, 16), rng.randint(1, 16)
        image = Image.new('RGBA', (width, height))
        for _ in range(rng.randint(1, 12)):
            image.putpixel((rng.randrange(width), rng.randrange(height)), (210, 50, 90, 255))
        x, y = rng.randint(-20, 50), rng.randint(-20, 50)
        angle = rng.choice((0, 30, 45, 90, 135, 180, 225, 270, 315))
        anchor = (rng.randint(0, width), rng.randint(0, height))
        if not destination_fits_canvas(image, x, y, angle, anchor, canvas):
            continue
        actual = Image.new('RGBA', canvas)
        actual.paste(image, (x, y))
        if angle:
            actual = actual.rotate(angle, Image.Resampling.NEAREST,
                                   center=(x + anchor[0], y + anchor[1]), expand=False)
        assert actual.getchannel('A').getbbox() is not None


def test_rgba_fast_path_does_not_convert_original_image(monkeypatch):
    image = Image.new('RGBA', (16, 16))
    image.putpixel((4, 4), (255, 0, 0, 255))
    def no_conversion(*args, **kwargs):
        raise AssertionError('RGBA destination must not be duplicated')
    monkeypatch.setattr(image, 'convert', no_conversion)
    assert destination_fits_canvas(image, 10, 10, 0, (8, 8), (64, 64))
    assert destination_fits_canvas(image, 10, 10, 90, (8, 8), (64, 64))
