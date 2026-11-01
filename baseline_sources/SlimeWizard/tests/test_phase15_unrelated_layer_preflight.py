"""Unrelated stale pose assets must not block safe Slimer source mapping."""
import ast
from pathlib import Path
from PIL import Image, ImageChops


def test_layered_plan_ignores_unselected_stale_asset():
    source = Path(__file__).resolve().parents[1] / 'friendly_animator.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and any(
        isinstance(m, ast.FunctionDef) and m.name == '_slimer_layered_erase_plan' for m in n.body))
    method = next(m for m in cls.body if isinstance(m, ast.FunctionDef) and m.name == '_slimer_layered_erase_plan')
    namespace = {'Image': Image, 'ImageChops': ImageChops}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(source), 'exec'), namespace)

    valid = Image.new('RGBA', (4, 4), (0, 0, 0, 0))
    valid.putpixel((0, 0), (255, 0, 0, 255))
    stale = Image.new('RGBA', (4, 4), (0, 0, 0, 0))
    stale.putpixel((3, 3), (0, 255, 0, 255))
    stale_cached = Image.new('RGBA', (4, 4), (0, 0, 255, 255))
    mask = Image.new('L', (4, 4), 0)
    mask.putpixel((0, 0), 255)

    class Model:
        size = (4, 4)
        originals = [valid, stale]
        parts = [{'image': valid}, {'image': stale_cached}]
        anchors = {0: [2, 2], 1: [2, 2]}
        def resolved_pose(self):
            return [dict(visible=True, x=0, y=0, width=4, height=4, angle=0),
                    dict(visible=True, x=0, y=0, width=4, height=4, angle=0)]
        def render_part(self, i, state):
            return self.originals[i]

    harness = type('Harness', (), {'model': Model()})()
    result = namespace['_slimer_layered_erase_plan'](harness, mask)
    assert result is not None
    assert [i for i, _ in result] == [0]
