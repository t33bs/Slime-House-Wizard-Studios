"""A translucent pixel hidden by opaque artwork must not veto another selected source pixel."""
import ast
from pathlib import Path
from PIL import Image, ImageChops


def test_occluded_translucent_pixel_is_not_selected_owner():
    path = Path(__file__).resolve().parents[1] / 'friendly_animator.py'
    tree = ast.parse(path.read_text(encoding='utf-8'))
    method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                  and n.name == '_slimer_layered_erase_plan')
    ns = {'Image': Image, 'ImageChops': ImageChops}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(path), 'exec'), ns)
    from studio.pet_suite_model import PetSuiteModel
    model = PetSuiteModel((16, 16))
    lower = Image.new('RGBA', (16, 16))
    lower.putpixel((2, 2), (255, 0, 0, 255))
    lower.putpixel((4, 4), (0, 0, 255, 128))
    upper = Image.new('RGBA', (16, 16))
    upper.putpixel((4, 4), (0, 255, 0, 255))
    model.import_part('lower mixed alpha', lower)
    model.import_part('upper opaque', upper)
    mask = Image.new('L', (16, 16))
    mask.putpixel((2, 2), 255)
    mask.putpixel((4, 4), 255)
    harness = type('Harness', (), {'model': model})()
    plan = ns['_slimer_layered_erase_plan'](harness, mask)
    assert plan is not None
    assert [i for i, _ in plan] == [0, 1]
    assert plan[0][1] == {2 + 2 * 16}
    assert plan[1][1] == {4 + 4 * 16}
    # Exposed translucent pixels over transparent background can safely move.
    upper.putpixel((4, 4), (0, 0, 0, 0))
    model.parts[1]['image'].putpixel((4, 4), (0, 0, 0, 0))
    model.originals[1].putpixel((4, 4), (0, 0, 0, 0))
    assert ns['_slimer_layered_erase_plan'](harness, mask) is not None
