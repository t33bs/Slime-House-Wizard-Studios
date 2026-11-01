"""A completely covered stale source must not veto the topmost selected pixels."""
import ast
from pathlib import Path
from PIL import Image, ImageChops


def test_occluded_stale_bottom_layer_does_not_block_top_layer():
    path = Path(__file__).resolve().parents[1] / 'friendly_animator.py'
    tree = ast.parse(path.read_text(encoding='utf-8'))
    method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == '_slimer_layered_erase_plan')
    ns = {'Image': Image, 'ImageChops': ImageChops}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(path), 'exec'), ns)
    bottom = Image.new('RGBA', (8, 8)); bottom.putpixel((2, 2), (255, 0, 0, 255))
    top = Image.new('RGBA', (8, 8)); top.putpixel((2, 2), (0, 255, 0, 255))
    stale = Image.new('RGBA', (8, 8), (0, 0, 255, 255))
    mask = Image.new('L', (8, 8)); mask.putpixel((2, 2), 255)
    class Model:
        size = (8, 8)
        originals = [bottom, top]
        parts = [{'image': stale}, {'image': top}]
        anchors = {0: [4, 4], 1: [4, 4]}
        def resolved_pose(self):
            return [dict(visible=True, x=0, y=0, width=8, height=8, angle=0) for _ in range(2)]
        def render_part(self, i, state):
            return self.originals[i]
    harness = type('Harness', (), {'model': Model()})()
    plan = ns['_slimer_layered_erase_plan'](harness, mask)
    assert plan is not None
    assert [i for i, _ in plan] == [1]
