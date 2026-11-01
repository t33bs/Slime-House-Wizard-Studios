"""An unselected upper layer must still occlude a scaled source footprint."""
import ast
from pathlib import Path
from PIL import Image, ImageChops


def test_unselected_occluder_preserves_complete_scaled_selection():
    path = Path(__file__).resolve().parents[1] / 'friendly_animator.py'
    tree = ast.parse(path.read_text(encoding='utf-8'))
    method = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == '_slimer_layered_erase_plan')
    ns = {'Image': Image, 'ImageChops': ImageChops}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(path), 'exec'), ns)
    bottom = Image.new('RGBA', (1, 1), (255, 0, 0, 255))
    upper = Image.new('RGBA', (8, 8))
    upper.putpixel((3, 2), (0, 255, 0, 255))
    mask = Image.new('L', (8, 8))
    mask.putpixel((2, 2), 255)

    class Model:
        size = (8, 8)
        originals = [bottom, upper]
        parts = [{'image': bottom.resize((2, 1), Image.Resampling.NEAREST)},
                 {'image': upper}]
        anchors = {0: [1, 0], 1: [4, 4]}

        def resolved_pose(self):
            return [dict(visible=True, x=2, y=2, width=2, height=1, angle=0),
                    dict(visible=True, x=0, y=0, width=8, height=8, angle=0)]

        def render_part(self, i, state):
            canvas = Image.new('RGBA', self.size)
            canvas.paste(self.parts[i]['image'], (state['x'], state['y']))
            return canvas

    plan = ns['_slimer_layered_erase_plan'](type('Harness', (), {'model': Model()})(), mask)
    assert plan == [(0, {0})]
