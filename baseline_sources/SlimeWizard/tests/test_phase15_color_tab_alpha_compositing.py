"""Regression: confirming color tabs must preserve semi-transparent artwork."""
from PIL import Image
import pytest
from studio.slimer_tool import composite_selection_layers


def test_single_translucent_pixel_preserves_alpha():
    layer = Image.new('RGBA', (8, 8))
    layer.putpixel((3, 4), (80, 120, 200, 96))
    combined = composite_selection_layers([layer], (8, 8))
    assert combined.getpixel((3, 4)) == (80, 120, 200, 96)


def test_overlapping_translucent_layers_use_source_over():
    first = Image.new('RGBA', (4, 4))
    second = Image.new('RGBA', (4, 4))
    first.putpixel((1, 1), (255, 0, 0, 128))
    second.putpixel((1, 1), (0, 0, 255, 128))
    expected = first.copy()
    expected.alpha_composite(second)
    assert composite_selection_layers([first, second], (4, 4)).tobytes() == expected.tobytes()


def test_mismatched_preview_rejected():
    with pytest.raises(ValueError, match='dimensions'):
        composite_selection_layers([Image.new('RGBA', (2, 2))], (4, 4))


def test_gui_confirm_uses_alpha_compositing_helper():
    import ast
    from pathlib import Path
    tree = ast.parse((Path(__file__).parents[1] / 'friendly_animator.py').read_text())
    fn = next(node for cls in tree.body if isinstance(cls, ast.ClassDef)
              for node in cls.body if isinstance(node, ast.FunctionDef)
              and node.name == 'slimer_confirm_all_placements')
    assert 'composite_selection_layers(layers, self.model.size)' in ast.unparse(fn)
