from PIL import Image
from studio.pixel_source_mapping import rendered_source_indices, selected_source_indices


def test_translated_mapping_preserves_source_index():
    mapping = rendered_source_indices((2, 2), (12, 12), 4, 5, 2, 2)
    assert mapping.getpixel((4, 5)) == 1
    assert mapping.getpixel((5, 6)) == 4
    assert mapping.getpixel((3, 5)) == 0


def test_rotated_mapping_matches_actual_nearest_renderer():
    from studio.pet_suite_model import PetSuiteModel
    source = Image.new('RGBA', (3, 2))
    colors = [(i + 1, 0, 0, 255) for i in range(6)]
    source.putdata(colors)
    model = PetSuiteModel((20, 20))
    model.import_part('test', source)
    for angle in (0, 45, 90, 135, 270):
        state = dict(x=7, y=8, width=6, height=4, angle=angle, visible=True)
        rendered = model.render_part(0, state)
        mapping = rendered_source_indices((3, 2), (20, 20), 7, 8, 6, 4, angle,
                                          anchor=(3, 2))
        for pixel, label in zip(rendered.get_flattened_data(), mapping.get_flattened_data()):
            assert pixel == (colors[label - 1] if label else (0, 0, 0, 0))


def test_selection_returns_unique_source_pixels_even_when_scaled():
    mapping = rendered_source_indices((2, 1), (10, 10), 2, 3, 6, 3)
    mask = Image.new('L', (10, 10), 0)
    mask.putpixel((2, 3), 255)
    mask.putpixel((4, 5), 255)
    assert selected_source_indices(mapping, mask) == {0}
