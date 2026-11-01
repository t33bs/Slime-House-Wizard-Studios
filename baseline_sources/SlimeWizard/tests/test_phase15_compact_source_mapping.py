"""Provenance mapping must remain pixel-exact without Python-int label lists."""
from PIL import Image
from studio.pixel_source_mapping import rendered_source_indices


def reference(source_size, canvas_size, x, y, width, height, angle=0, anchor=None):
    sw, sh = source_size
    labels = Image.new('I', (sw, sh))
    labels.putdata(list(range(1, sw * sh + 1)))
    scaled = labels.resize((width, height), Image.Resampling.NEAREST)
    canvas = Image.new('I', canvas_size, 0)
    canvas.paste(scaled, (x, y))
    if angle % 360:
        if anchor is None:
            anchor = (width // 2, height // 2)
        canvas = canvas.rotate(angle, Image.Resampling.NEAREST,
                               center=(x + anchor[0], y + anchor[1]), expand=False)
    return canvas


def test_compact_mapping_matches_original_for_scaled_rotated_and_clipped():
    cases = [((3, 4), (14, 12), 2, 1, 7, 8, 0, None),
             ((5, 3), (12, 15), -2, 4, 10, 6, 90, (3, 2)),
             ((6, 6), (13, 13), 5, -3, 3, 9, 45, None),
             ((8, 7), (4, 5), -2, -1, 8, 7, 180, None)]
    for args in cases:
        actual = rendered_source_indices(*args)
        expected = reference(*args)
        assert actual.tobytes() == expected.tobytes()


def test_large_1024_source_has_correct_end_labels():
    mapping = rendered_source_indices((1024, 1024), (1024, 1024), 0, 0, 1024, 1024)
    assert mapping.getpixel((0, 0)) == 1
    assert mapping.getpixel((1023, 1023)) == 1024 * 1024
    assert mapping.getpixel((400, 700)) == 700 * 1024 + 401
