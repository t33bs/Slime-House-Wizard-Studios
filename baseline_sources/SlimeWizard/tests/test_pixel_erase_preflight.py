from PIL import Image
import pytest
from studio.pixel_source_mapping import (rendered_source_indices,
    plan_complete_source_erase, erase_planned_source_pixels)


def test_enlarged_pixel_requires_complete_visible_footprint():
    mapping = rendered_source_indices((1, 1), (8, 8), 2, 2, 3, 3)
    alpha = Image.new('L', (8, 8), 255)
    mask = Image.new('L', (8, 8), 0)
    mask.putpixel((2, 2), 255)
    assert plan_complete_source_erase(mapping, alpha, mask) is None
    for y in range(2, 5):
        for x in range(2, 5):
            mask.putpixel((x, y), 255)
    assert plan_complete_source_erase(mapping, alpha, mask) == {0}


def test_rotated_full_footprint_is_eligible_and_partial_is_not():
    mapping = rendered_source_indices((2, 2), (14, 14), 5, 5, 4, 4, 45)
    alpha = Image.new('L', (14, 14), 255)
    mask = Image.new('L', (14, 14), 0)
    for y in range(14):
        for x in range(14):
            if mapping.getpixel((x, y)) == 1:
                mask.putpixel((x, y), 255)
    assert plan_complete_source_erase(mapping, alpha, mask) == {0}
    locations = [(x, y) for y in range(14) for x in range(14) if mapping.getpixel((x, y)) == 1]
    assert len(locations) > 1
    mask.putpixel(locations[0], 0)
    assert plan_complete_source_erase(mapping, alpha, mask) is None


def test_erase_returns_copy_preserving_other_pixels_and_alpha():
    source = Image.new('RGBA', (2, 1))
    source.putdata([(20, 40, 60, 128), (80, 100, 120, 255)])
    changed = erase_planned_source_pixels(source, {0})
    assert source.getpixel((0, 0)) == (20, 40, 60, 128)
    assert changed.getpixel((0, 0)) == (0, 0, 0, 0)
    assert changed.getpixel((1, 0)) == source.getpixel((1, 0))
    with pytest.raises(ValueError):
        erase_planned_source_pixels(source, {2})
    assert source.getpixel((1, 0)) == (80, 100, 120, 255)
