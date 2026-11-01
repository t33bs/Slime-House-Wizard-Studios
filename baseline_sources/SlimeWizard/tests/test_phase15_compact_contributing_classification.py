from PIL import Image
from studio.pixel_source_mapping import classify_contributing_source_selection


def test_large_canvas_sparse_selection_and_opaque_occlusion():
    size = (1024, 1024)
    bottom = Image.new('I', size, 0)
    bottom.putpixel((10, 10), 1)
    bottom.putpixel((11, 10), 1)
    top = Image.new('I', size, 0)
    top.putpixel((11, 10), 1)
    bottom_alpha = Image.new('L', size, 0)
    bottom_alpha.putpixel((10, 10), 255)
    bottom_alpha.putpixel((11, 10), 255)
    top_alpha = Image.new('L', size, 0)
    top_alpha.putpixel((11, 10), 255)
    selection = Image.new('L', size, 0)
    selection.putpixel((10, 10), 255)
    assert classify_contributing_source_selection(
        [(bottom, bottom_alpha), (top, top_alpha)], selection
    ) == [({0}, set()), (set(), set())]


def test_partial_alpha_overlay_does_not_hide_unselected_source_occurrence():
    size = (3, 1)
    bottom = Image.new('I', size)
    bottom.putdata([1, 1, 0])
    top = Image.new('I', size)
    top.putdata([0, 1, 0])
    a = Image.new('L', size)
    a.putdata([255, 255, 0])
    b = Image.new('L', size)
    b.putdata([0, 128, 0])
    mask = Image.new('L', size)
    mask.putdata([255, 0, 0])
    assert classify_contributing_source_selection([(bottom, a), (top, b)], mask) == [
        (set(), {0}), (set(), set())
    ]
