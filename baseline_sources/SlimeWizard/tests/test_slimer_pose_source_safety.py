"""Guard destructive Slimer moves against mismatched pose source buffers."""
from pathlib import Path
import ast
from types import SimpleNamespace
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


def method(name):
    path = Path(__file__).resolve().parents[1] / 'friendly_animator.py'
    tree = ast.parse(path.read_text())
    node = next(n for c in tree.body if isinstance(c, ast.ClassDef)
                for n in c.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), env := {'Image': Image})
    return env[name]


def test_saved_pose_source_mismatch_blocks_destructive_move():
    model = PetSuiteModel((8, 8))
    model.import_part('cat', Image.new('RGBA', (2, 2), 'red'))
    state = model.resolved_pose()[0]
    state['source_png'] = model._encode_source(Image.new('RGBA', (2, 2), 'blue'))
    model.resolved_pose = lambda: [state]
    assert method('_slimer_original_erase_safe')(SimpleNamespace(model=model)) is False


def test_current_source_still_allows_destructive_move():
    model = PetSuiteModel((8, 8))
    model.import_part('cat', Image.new('RGBA', (2, 2), 'red'))
    assert method('_slimer_original_erase_safe')(SimpleNamespace(model=model)) is True


def test_resolved_visibility_controls_which_layer_gets_erased():
    model = PetSuiteModel((8, 8))
    model.import_part('bottom', Image.new('RGBA', (1, 1), 'red'))
    model.import_part('top', Image.new('RGBA', (1, 1), 'blue'))
    states = model.resolved_pose()
    states[1]['visible'] = False
    model.resolved_pose = lambda: states
    mask = Image.new('L', (8, 8), 0)
    mask.putpixel((0, 0), 255)
    method('_slimer_erase_original_layers')(SimpleNamespace(model=model), mask)
    assert model.parts[0]['image'].getpixel((0, 0))[3] == 0
    assert model.parts[1]['image'].getpixel((0, 0))[3] == 255


def test_pose_source_matching_part_but_not_original_is_blocked():
    model = PetSuiteModel((8, 8))
    model.import_part('cat', Image.new('RGBA', (2, 2), 'red'))
    # A stale part image can match a pose-local source while the original
    # backing buffer still belongs to a different pose.
    model.parts[0]['image'] = Image.new('RGBA', (2, 2), 'blue')
    state = model.resolved_pose()[0]
    state['source_png'] = model._encode_source(model.parts[0]['image'])
    model.resolved_pose = lambda: [state]
    assert method('_slimer_original_erase_safe')(SimpleNamespace(model=model)) is False


def test_matching_pose_source_and_both_edit_buffers_remains_safe():
    model = PetSuiteModel((8, 8))
    model.import_part('cat', Image.new('RGBA', (2, 2), 'red'))
    assert method('_slimer_original_erase_safe')(SimpleNamespace(model=model)) is True
