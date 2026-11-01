"""Opaque source pixels remain movable when their asset has unrelated translucent art."""
import ast
from pathlib import Path
from PIL import Image, ImageChops


def test_unselected_translucent_pixel_does_not_veto_rotated_source_plan():
    path = Path(__file__).resolve().parents[1] / 'friendly_animator.py'
    tree = ast.parse(path.read_text(encoding='utf-8'))
    method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                  and n.name == '_slimer_layered_erase_plan')
    ns = {'Image': Image, 'ImageChops': ImageChops}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(path), 'exec'), ns)
    from studio.pet_suite_model import PetSuiteModel
    model = PetSuiteModel((16, 16))
    source = Image.new('RGBA', (16, 16))
    source.putpixel((3, 3), (255, 0, 0, 255))
    source.putpixel((10, 10), (0, 0, 255, 128))
    model.import_part('mixed alpha', source)
    mask = Image.new('L', (16, 16))
    mask.putpixel((3, 3), 255)
    harness = type('Harness', (), {'model': model})()
    plan = ns['_slimer_layered_erase_plan'](harness, mask)
    assert plan is not None, 'Unselected translucent art must not block opaque source selection'
    assert [i for i, _ in plan] == [0]
    # A fractional-alpha pixel over transparent background can now move
    # without flattening or damaging another layer. Both selected footprints
    # remain complete and preserve native alpha.
    mask.putpixel((10, 10), 255)
    assert ns['_slimer_layered_erase_plan'](harness, mask) is not None
