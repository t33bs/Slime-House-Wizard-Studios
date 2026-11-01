"""Run two actual Slimer source erasures against the real editable model.

No Qt dependency: exercises the production planner and eraser through their AST.
"""
import ast
from pathlib import Path
from PIL import Image, ImageChops
from studio.pet_suite_model import PetSuiteModel


def test_two_consecutive_move_original_erasures_keep_independent_layers():
    path = Path(__file__).resolve().parents[1] / 'friendly_animator.py'
    tree = ast.parse(path.read_text(encoding='utf-8'))
    methods = {node.name: node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    names = ('_slimer_layered_erase_plan', '_slimer_transformed_erase_plan', '_slimer_erase_original_layers')
    scope = {'Image': Image, 'ImageChops': ImageChops}
    exec(compile(ast.Module(body=[methods[n] for n in names], type_ignores=[]), str(path), 'exec'), scope)

    model = PetSuiteModel((16, 16))
    base = Image.new('RGBA', (16, 16))
    base.putpixel((2, 2), (250, 30, 30, 255))
    base.putpixel((5, 5), (30, 250, 30, 255))
    model.import_part('base', base)

    class Harness:
        _slimer_layered_erase_plan = scope['_slimer_layered_erase_plan']
        _slimer_transformed_erase_plan = scope['_slimer_transformed_erase_plan']
        _slimer_erase_original_layers = scope['_slimer_erase_original_layers']
        def __init__(self, model):
            self.model = model

    harness = Harness(model)
    for number, (source_x, source_y, dest_x, dest_y) in enumerate(((2, 2, 8, 8), (5, 5, 11, 11)), 1):
        mask = Image.new('L', model.size, 0)
        mask.putpixel((source_x, source_y), 255)
        before = model.render().copy()
        extracted = Image.new('RGBA', model.size)
        extracted.putpixel((source_x, source_y), before.getpixel((source_x, source_y)))
        model.import_part(f'Slimer Layer {number:03}', extracted)
        staged = model.parts[-1]
        staged['x'], staged['y'] = dest_x-source_x, dest_y-source_y
        staged['visible'] = False
        assert model.render().tobytes() == before.tobytes()
        assert harness._slimer_layered_erase_plan(mask) is not None
        harness._slimer_erase_original_layers(mask)
        staged['visible'] = True
        assert model.render().getpixel((dest_x, dest_y)) == before.getpixel((source_x, source_y))
        assert model.render().getpixel((source_x, source_y))[3] == 0
        assert model.render().getpixel((5, 5))[3] == (255 if number == 1 else 0)
    assert len(model.parts) == 3
    assert model.render().getpixel((8, 8)) == (250, 30, 30, 255)
    assert model.render().getpixel((11, 11)) == (30, 250, 30, 255)
