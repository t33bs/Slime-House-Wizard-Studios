"""Single-layer transformed fallback must preserve live geometry and alpha safety."""
from test_slimer_transformed_integration import method, setup
from PIL import Image


def test_scaled_fallback_retains_display_dimensions_after_source_erase():
    obj = setup()
    # The live display buffer is nearest-neighbor scaled to 3x3.
    obj.model.resize_part(0, 3, 3)
    mask = Image.new('L', (12, 12), 0)
    mask.paste(255, (3, 3, 6, 6))
    obj._slimer_layered_erase_plan = lambda mask: None
    method('_slimer_erase_original_layers')(obj, mask)
    assert obj.model.parts[0]['image'].size == (3, 3)
    assert obj.model.originals[0].size == (1, 1)
    assert obj.model.originals[0].getpixel((0, 0)) == (0, 0, 0, 0)
