"""Partial alpha above an enlarged pixel must not conceal its visible footprint."""
import ast
from pathlib import Path
from PIL import Image, ImageChops
from studio.pet_suite_model import PetSuiteModel


def test_translucent_occluder_does_not_authorize_erasing_visible_lower_pixel():
    path = Path(__file__).resolve().parents[1] / 'friendly_animator.py'
    tree = ast.parse(path.read_text(encoding='utf-8'))
    method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                  and n.name == '_slimer_layered_erase_plan')
    ns = {'Image': Image, 'ImageChops': ImageChops}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(path), 'exec'), ns)
    model = PetSuiteModel((16, 16))
    lower = Image.new('RGBA', (1, 1), (255, 0, 0, 255))
    model.import_part('enlarged lower', lower)
    model.resize_part(0, 2, 1)
    model.parts[0]['x'] = 2
    model.parts[0]['y'] = 2
    upper = Image.new('RGBA', (16, 16))
    upper.putpixel((3, 2), (0, 0, 255, 128))
    model.import_part('translucent upper', upper)
    mask = Image.new('L', (16, 16))
    mask.putpixel((2, 2), 255)
    harness = type('Harness', (), {'model': model})()
    # The lower source pixel still contributes through the translucent upper
    # pixel at (3,2). Erasing it would alter unselected visible artwork.
    assert ns['_slimer_layered_erase_plan'](harness, mask) is None
    # An opaque upper layer *does* fully conceal that occurrence.
    model.originals[1].putpixel((3, 2), (0, 0, 255, 255))
    model.parts[1]['image'].putpixel((3, 2), (0, 0, 255, 255))
    plan = ns['_slimer_layered_erase_plan'](harness, mask)
    assert plan is not None
    assert plan[0] == (0, {0})
