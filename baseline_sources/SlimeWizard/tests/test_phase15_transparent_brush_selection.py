"""Phase 52: brush strokes through transparent canvas must not veto a move."""
import ast
from pathlib import Path
from PIL import Image

SOURCE = Path(__file__).resolve().parents[1] / 'friendly_animator.py'
tree = ast.parse(SOURCE.read_text())
methods = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == '_slimer_visible_selection_mask']
assert len(methods) == 1
method = methods[0]
method.decorator_list = []
ns = {}
exec(compile(ast.Module(body=[method], type_ignores=[]), str(SOURCE), 'exec'), ns)
visible_mask = ns['_slimer_visible_selection_mask']


def test_selection_across_transparent_background_only_targets_artwork():
    canvas = Image.new('RGBA', (8, 8))
    canvas.putpixel((2, 2), (255, 0, 0, 255))
    canvas.putpixel((3, 2), (0, 255, 0, 128))
    mask = Image.new('L', (8, 8))
    for x in range(1, 6):
        mask.putpixel((x, 2), 255)
    actual = visible_mask(mask, canvas)
    assert actual.getbbox() == (2, 2, 4, 3)
    assert actual.getpixel((1, 2)) == 0
    assert actual.getpixel((2, 2)) == 255
    assert actual.getpixel((3, 2)) == 255
    assert actual.getpixel((4, 2)) == 0


def test_empty_background_only_selection_stays_empty():
    assert visible_mask(Image.new('L', (4, 4), 255), Image.new('RGBA', (4, 4))).getbbox() is None


def test_mismatched_dimensions_are_rejected():
    import pytest
    with pytest.raises(ValueError):
        visible_mask(Image.new('L', (3, 3)), Image.new('RGBA', (4, 4)))


def test_edit_selection_uses_effective_mask_for_preflight_and_commit():
    text = SOURCE.read_text()
    start = text.index('    def slimer_create_editable_layer(')
    end = text.index('    def slimer_cancel_editable_layer(', start)
    body = text[start:end]
    assert '_slimer_original_erase_safe(effective_mask)' in body
    assert 'self._slimer_pending_mask=effective_mask.copy()' in body
    assert "ImageChops.multiply(source.getchannel('A'), effective_mask)" in body
