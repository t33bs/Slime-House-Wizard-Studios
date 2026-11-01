"""Headless regression for overlapping source layers during Move Original."""
import ast
from pathlib import Path
from types import SimpleNamespace
from PIL import Image


def test_move_original_preserves_covered_lower_layer():
    source = Path(__file__).resolve().parents[1] / 'friendly_animator.py'
    tree = ast.parse(source.read_text())
    method = next(n for cls in tree.body if isinstance(cls, ast.ClassDef)
                  for n in cls.body if isinstance(n, ast.FunctionDef)
                  if n.name == '_slimer_erase_original_layers')
    method.decorator_list = []
    namespace = {'Image': Image}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(source), 'exec'), namespace)
    bottom = Image.new('RGBA', (4, 4)); bottom.putpixel((1, 1), (255, 0, 0, 255))
    top = Image.new('RGBA', (4, 4)); top.putpixel((1, 1), (0, 0, 255, 255))
    model = SimpleNamespace(size=(4, 4), parts=[
        {'image': bottom, 'x': 0, 'y': 0, 'visible': True},
        {'image': top, 'x': 0, 'y': 0, 'visible': True}],
        originals=[bottom.copy(), top.copy()],
        resolved_pose=lambda: [{'x': 0, 'y': 0}, {'x': 0, 'y': 0}])
    mask = Image.new('L', (4, 4), 0); mask.putpixel((1, 1), 255)
    namespace['_slimer_erase_original_layers'](SimpleNamespace(model=model), mask)
    assert model.parts[0]['image'].getpixel((1, 1)) == (255, 0, 0, 255)
    assert model.parts[1]['image'].getpixel((1, 1))[3] == 0
