"""Headless integration checks for guarded transformed source erasure."""
import ast
from pathlib import Path
from types import SimpleNamespace
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


def method(name):
    path = Path(__file__).resolve().parents[1] / 'friendly_animator.py'
    tree = ast.parse(path.read_text())
    node = next(n for c in tree.body if isinstance(c, ast.ClassDef)
                for n in c.body if isinstance(n, ast.FunctionDef) and n.name == name)
    namespace = {'Image': Image}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), namespace)
    return namespace[name]


def setup():
    model = PetSuiteModel((12, 12))
    model.import_part('sprite', Image.new('RGBA', (1, 1), (255, 0, 0, 128)))
    state = model.resolved_pose()[0]
    state.update(x=3, y=3, width=3, height=3)
    state.pop('source_png', None)  # Explicit live-source pose; saved-source poses remain guarded
    model.resolved_pose = lambda: [state]
    obj = SimpleNamespace(model=model)
    obj._slimer_transformed_erase_plan = lambda mask: method('_slimer_transformed_erase_plan')(obj, mask)
    return obj


def test_full_scaled_selection_can_erase_source():
    obj = setup()
    mask = Image.new('L', (12, 12), 0)
    mask.paste(255, (3, 3, 6, 6))
    assert method('_slimer_original_erase_safe')(obj, mask)
    method('_slimer_erase_original_layers')(obj, mask)
    assert obj.model.originals[0].getpixel((0, 0)) == (0, 0, 0, 0)


def test_partial_scaled_selection_stays_blocked():
    obj = setup()
    mask = Image.new('L', (12, 12), 0)
    mask.putpixel((3, 3), 255)
    assert method('_slimer_transformed_erase_plan')(obj, mask) is None
    assert not method('_slimer_original_erase_safe')(obj, mask)


def test_second_visible_layer_blocks_transformed_plan():
    obj = setup()
    obj.model.import_part('other', Image.new('RGBA', (1, 1), 'blue'))
    states = obj.model.resolved_pose()
    states.append({'x': 0, 'y': 0, 'width': 1, 'height': 1, 'angle': 0, 'visible': True})
    obj.model.resolved_pose = lambda: states
    mask = Image.new('L', (12, 12), 255)
    assert method('_slimer_transformed_erase_plan')(obj, mask) is None
