from PIL import Image
import pytest
from studio.pixel_source_mapping import rendered_source_indices, classify_topmost_source_selection


def test_overlapping_layers_selects_only_topmost_source():
    mapping = rendered_source_indices((1, 1), (2, 2), 0, 0, 2, 2)
    alpha = Image.new('L', (2, 2), 255)
    mask = Image.new('L', (2, 2), 255)
    assert classify_topmost_source_selection([(mapping, alpha), (mapping, alpha)], mask) == [
        (set(), set()), ({0}, set())]


def test_partially_occluded_scaled_pixel_classified_by_exposed_footprint():
    bottom = rendered_source_indices((1, 1), (2, 2), 0, 0, 2, 2)
    top = rendered_source_indices((1, 1), (2, 2), 0, 0, 1, 1)
    alpha = Image.new('L', (2, 2), 255)
    top_alpha = Image.new('L', (2, 2), 0)
    top_alpha.putpixel((0, 0), 255)
    mask = Image.new('L', (2, 2), 255)
    mask.putpixel((0, 0), 0)
    assert classify_topmost_source_selection([(bottom, alpha), (top, top_alpha)], mask) == [
        ({0}, set()), (set(), set())]


def test_clipped_footprint_only_counts_on_canvas():
    mapping = rendered_source_indices((1, 1), (2, 2), 1, 1, 3, 3)
    alpha = Image.new('L', (2, 2), 255)
    mask = Image.new('L', (2, 2), 0)
    mask.putpixel((1, 1), 255)
    assert classify_topmost_source_selection([(mapping, alpha)], mask) == [({0}, set())]


def test_inherited_rotation_mapping_requires_resolved_coordinates():
    # The mapping utility consumes resolved coordinates, not local child offsets.
    mapping = rendered_source_indices((2, 1), (8, 8), 3, 2, 2, 1, 90)
    assert mapping.getbbox() is not None
    mask = mapping.point(lambda p: 255 if p else 0).convert('L')
    alpha = mask.copy()
    assert classify_topmost_source_selection([(mapping, alpha)], mask) == [({0, 1}, set())]


def test_mismatched_layer_dimensions_refused():
    mapping = Image.new('I', (2, 2), 1)
    with pytest.raises(ValueError):
        classify_topmost_source_selection([(mapping, Image.new('L', (3, 2)))], Image.new('L', (2, 2)))
