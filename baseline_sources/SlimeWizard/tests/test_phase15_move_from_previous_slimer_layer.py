"""A second Move Original may select artwork from a previously moved Slimer asset."""
import ast
from pathlib import Path
from PIL import Image, ImageChops
from studio.pet_suite_model import PetSuiteModel


def test_move_again_from_previous_slimer_layer():
    path = Path(__file__).resolve().parents[1] / 'friendly_animator.py'
    tree = ast.parse(path.read_text(encoding='utf-8'))
    methods = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
    names = ('_slimer_layered_erase_plan', '_slimer_transformed_erase_plan', '_slimer_erase_original_layers')
    scope = {'Image': Image, 'ImageChops': ImageChops}
    exec(compile(ast.Module(body=[methods[n] for n in names], type_ignores=[]), str(path), 'exec'), scope)

    class Harness:
        _slimer_layered_erase_plan = scope['_slimer_layered_erase_plan']
        _slimer_transformed_erase_plan = scope['_slimer_transformed_erase_plan']
        _slimer_erase_original_layers = scope['_slimer_erase_original_layers']
        def __init__(self, model): self.model = model

    model = PetSuiteModel((16, 16))
    original = Image.new('RGBA', model.size)
    original.putpixel((2, 2), (120, 220, 50, 255))
    model.import_part('base', original)
    harness = Harness(model)
    for number, (sx, sy, dx, dy) in enumerate(((2, 2, 8, 8), (8, 8, 12, 12)), 1):
        before = model.render()
        mask = Image.new('L', model.size)
        mask.putpixel((sx, sy), 255)
        isolated = Image.new('RGBA', model.size)
        isolated.putpixel((sx, sy), before.getpixel((sx, sy)))
        model.import_part(f'Slimer Layer {number}', isolated)
        staged = model.parts[-1]
        staged['x'], staged['y'] = dx-sx, dy-sy
        staged['visible'] = False
        assert harness._slimer_layered_erase_plan(mask) is not None
        harness._slimer_erase_original_layers(mask)
        staged['visible'] = True
        assert model.render().getpixel((sx, sy))[3] == 0
        assert model.render().getpixel((dx, dy)) == (120, 220, 50, 255)
    assert model.render().getpixel((12, 12)) == (120, 220, 50, 255)
