"""Phase 72: cropped alpha rotation must match the full-surface reference."""
import random
from PIL import Image
from studio.slimer_destination import destination_fits_canvas


def reference(image, x, y, angle, anchor, canvas_size):
    alpha = image.getchannel('A')
    bbox = alpha.getbbox()
    if bbox is None:
        return False
    w, h = image.size
    rotated = float(angle) % 360 != 0
    if rotated:
        l, t, r, b = bbox
        if x + l < 0 or y + t < 0 or x + r > canvas_size[0] or y + b > canvas_size[1]:
            return False
        ax, ay = anchor
        pad = int(max(w, h, abs(ax), abs(ay), abs(w-ax), abs(h-ay)) * 3 + 4)
        surface = Image.new('L', (w + 2*pad, h + 2*pad))
        surface.paste(alpha, (pad, pad))
        alpha = surface.rotate(float(angle), Image.Resampling.NEAREST,
                               center=(pad + ax, pad + ay), expand=False)
        x, y = x-pad, y-pad
    bbox = alpha.getbbox()
    if bbox is None:
        return False
    l, t, r, b = bbox
    return x+l >= 0 and y+t >= 0 and x+r <= canvas_size[0] and y+b <= canvas_size[1]


def test_cropped_rotation_matches_full_surface_reference():
    rng = random.Random(7201)
    for _ in range(500):
        w, h = rng.randint(3, 75), rng.randint(3, 75)
        image = Image.new('RGBA', (w, h))
        for _ in range(rng.randint(1, 8)):
            image.putpixel((rng.randrange(w), rng.randrange(h)), (1, 2, 3, 255))
        x, y = rng.randint(-20, 60), rng.randint(-20, 60)
        angle = rng.choice((0, 17, 45, 90, 135, 180, 270, 315))
        anchor = (rng.randint(-10, w+10), rng.randint(-10, h+10))
        assert destination_fits_canvas(image, x, y, angle, anchor, (90, 90)) == reference(image, x, y, angle, anchor, (90, 90))


def test_large_transparent_staged_layer_matches_reference():
    image = Image.new('RGBA', (1024, 1024))
    for px in ((510, 510), (512, 511), (513, 513)):
        image.putpixel(px, (255, 255, 255, 255))
    for angle in (30, 90, 180, 270):
        for x, y in ((0, 0), (-500, -500), (10, 10)):
            assert destination_fits_canvas(image, x, y, angle, (512, 512), (1024, 1024)) == reference(image, x, y, angle, (512, 512), (1024, 1024))
