"""Move Original must not silently erase translucent source pixels."""
import ast
from pathlib import Path
from PIL import Image, ImageChops


def test_translucent_selected_pixel_rejected_by_fallback():
    path = Path(__file__).resolve().parents[1] / 'friendly_animator.py'
    tree = ast.parse(path.read_text(encoding='utf-8'))
    cls = next(c for c in tree.body if isinstance(c, ast.ClassDef)
               and any(isinstance(m, ast.FunctionDef) and m.name == '_slimer_original_erase_safe' for m in c.body))
    method = next(m for m in cls.body if isinstance(m, ast.FunctionDef) and m.name == '_slimer_original_erase_safe')
    ns = {'ImageChops': ImageChops}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(path), 'exec'), ns)
    source = Image.new('RGBA', (2, 2), (0, 0, 0, 0))
    source.putpixel((0, 0), (255, 0, 0, 128))
    mask = Image.new('L', (2, 2), 0)
    mask.putpixel((0, 0), 255)
    class Model:
        size = (2, 2)
        originals = [source]
        parts = [{'image': source, 'name': 'Artwork'}]
        def resolved_pose(self):
            return [dict(visible=True, x=0, y=0, width=2, height=2, angle=0)]
        def render_part(self, i, state):
            return source
    obj = type('Harness', (), {'model': Model(),
        '_slimer_layered_erase_plan': lambda self, m: None,
        '_slimer_transformed_erase_plan': lambda self, m: None})()
    assert ns['_slimer_original_erase_safe'](obj, mask) is False
    source.putpixel((0, 0), (255, 0, 0, 255))
    assert ns['_slimer_original_erase_safe'](obj, mask) is True
