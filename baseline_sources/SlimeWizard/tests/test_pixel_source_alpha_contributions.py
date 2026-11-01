import pytest
from PIL import Image
from studio.pixel_source_mapping import classify_contributing_source_selection


def test_partial_alpha_top_does_not_hide_lower_contribution():
    mapping = Image.new('I', (1, 1), 1)
    selection = Image.new('L', (1, 1), 255)
    layers = [(mapping, Image.new('L', (1, 1), 255)),
              (mapping, Image.new('L', (1, 1), 128))]
    assert classify_contributing_source_selection(layers, selection) == [({0}, set()), ({0}, set())]


def test_opaque_top_hides_lower_contribution():
    mapping = Image.new('I', (1, 1), 1)
    selected = Image.new('L', (1, 1), 255)
    layers = [(mapping, Image.new('L', (1, 1), 255)),
              (mapping, Image.new('L', (1, 1), 255))]
    assert classify_contributing_source_selection(layers, selected) == [(set(), set()), ({0}, set())]


def test_partial_footprint_stays_partial_under_translucent_cover():
    mapping = Image.new('I', (2, 1)); mapping.putdata([1, 1])
    selection = Image.new('L', (2, 1)); selection.putdata([255, 0])
    upper = Image.new('L', (2, 1)); upper.putdata([128, 0])
    layers = [(mapping, Image.new('L', (2, 1), 255)), (mapping, upper)]
    assert classify_contributing_source_selection(layers, selection) == [(set(), {0}), ({0}, set())]


def test_dimension_mismatch_rejected():
    with pytest.raises(ValueError):
        classify_contributing_source_selection([(Image.new('I', (2, 2)), Image.new('L', (1, 1)))], Image.new('L', (2, 2)))
