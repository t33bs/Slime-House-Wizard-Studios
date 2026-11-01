"""Phase 85: resize only selected content, with alpha, baseline, and clipping safety."""
import pytest
from PIL import Image
from studio.slimer_asset_scale import scaled_selection_content


def _image():
    image = Image.new('RGBA', (128, 128))
    image.putpixel((40, 50), (255, 22, 13, 255))
    image.putpixel((41, 50), (20, 200, 30, 144))
    image.putpixel((40, 51), (35, 55, 245, 255))
    image.putpixel((41, 51), (200, 200, 80, 144))
    return image


def test_staged_asset_scales_its_occupied_pixels_not_the_full_transparent_canvas():
    original = _image()
    two_hundred = scaled_selection_content(original, 200, (41, 51))
    assert two_hundred.size == original.size == (128, 128)
    assert two_hundred.getchannel('A').getbbox() == (39, 49, 43, 53)
    assert two_hundred.getpixel((39, 49)) == (255, 22, 13, 255)
    assert two_hundred.getpixel((42, 49)) == (20, 200, 30, 144)
    assert two_hundred.getpixel((0, 0))[3] == 0
    assert original.getchannel('A').getbbox() == (40, 50, 42, 52)


def test_percent_recomputed_from_same_source_does_not_accumulate_pixel_loss():
    original = _image()
    expanded = scaled_selection_content(original, 300, (41, 51))
    assert expanded.getchannel('A').getbbox() is not None
    restored = scaled_selection_content(original, 100, (41, 51))
    assert restored.tobytes() == original.tobytes()


def test_outside_canvas_resizing_is_rejected_before_mutating_any_pixel():
    original = Image.new('RGBA', (128, 128))
    original.putpixel((126, 126), (200, 10, 10, 255))
    original.putpixel((127, 127), (5, 200, 5, 255))
    untouched = original.tobytes()
    with pytest.raises(ValueError, match='canvas edge'):
        scaled_selection_content(original, 300, (126, 126))
    assert original.tobytes() == untouched


def test_translucent_selected_colors_survive_resize_exactly():
    original = _image()
    scaled = scaled_selection_content(original, 200, (41, 51))
    assert scaled.getpixel((42, 49)) == (20, 200, 30, 144)
    assert scaled.getpixel((42, 52)) == (200, 200, 80, 144)
