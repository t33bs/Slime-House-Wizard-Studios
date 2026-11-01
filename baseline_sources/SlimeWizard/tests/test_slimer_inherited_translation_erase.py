"""Exact canvas-to-source mapping for attached, translated layers."""
import ast
from pathlib import Path
from types import SimpleNamespace
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


def _method(name):
    source = Path(__file__).resolve().parents[1] / 'friendly_animator.py'
    tree = ast.parse(source.read_text())
    method = next(n for cls in tree.body if isinstance(cls, ast.ClassDef)
                  for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    method.decorator_list = []
    scope = {'Image': Image}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(source), 'exec'), scope)
    return scope[name]


def test_inherited_translation_erases_correct_source_pixel():
    model = PetSuiteModel((12, 12))
    parent = Image.new('RGBA', (1, 1), (255, 0, 0, 255))
    child = Image.new('RGBA', (2, 2), (0, 0, 0, 0))
    child.putpixel((0, 0), (0, 255, 0, 255))
    model.import_part('parent', parent)
    model.import_part('child', child)
    model.parts[0]['x'] = 1
    model.parts[1]['x'] = 3
    # Simulate a resolved attachment offset, independent of raw part coordinates.
    resolve = model.resolved_pose
    def translated_pose():
        states = resolve()
        states[1]['x'] = 6
        return states
    model.resolved_pose = translated_pose
    editor = SimpleNamespace(model=model)
    assert _method('_slimer_original_erase_safe')(editor)
    mask = Image.new('L', (12, 12), 0)
    mask.putpixel((6, 0), 255)
    _method('_slimer_erase_original_layers')(editor, mask)
    assert model.parts[1]['image'].getpixel((0, 0))[3] == 0
    assert model.parts[0]['image'].getpixel((0, 0))[3] == 255
