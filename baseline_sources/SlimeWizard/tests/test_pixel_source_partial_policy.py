from PIL import Image
import pytest
from studio.pixel_source_mapping import rendered_source_indices, classify_source_selection


def test_partial_scaled_pixel_cannot_be_erased():
    mapping = rendered_source_indices((1, 1), (8, 8), 2, 2, 3, 3)
    mask = Image.new('L', (8, 8), 0)
    mask.putpixel((2, 2), 255)
    assert classify_source_selection(mapping, mask) == (set(), {0})
    for y in range(2, 5):
        for x in range(2, 5):
            mask.putpixel((x, y), 255)
    assert classify_source_selection(mapping, mask) == ({0}, set())


def test_independent_source_pixels_are_classified_separately():
    mapping = rendered_source_indices((2, 1), (8, 8), 1, 1, 4, 2)
    mask = Image.new('L', (8, 8), 0)
    for y in (1, 2):
        for x in (1, 2):
            mask.putpixel((x, y), 255)
    mask.putpixel((3, 1), 255)
    assert classify_source_selection(mapping, mask) == ({0}, {1})


def test_transparent_occurrences_are_ignored():
    mapping = rendered_source_indices((1, 1), (8, 8), 2, 2, 2, 2)
    mask = Image.new('L', (8, 8), 0)
    alpha = Image.new('L', (8, 8), 0)
    mask.putpixel((2, 2), 255)
    alpha.putpixel((2, 2), 255)
    assert classify_source_selection(mapping, mask, alpha) == ({0}, set())


def test_mismatched_mask_or_alpha_rejected():
    mapping = rendered_source_indices((1, 1), (8, 8), 0, 0, 1, 1)
    with pytest.raises(ValueError):
        classify_source_selection(mapping, Image.new('L', (7, 8)))
    with pytest.raises(ValueError):
        classify_source_selection(mapping, Image.new('L', (8, 8)), Image.new('L', (8, 7)))
