"""Creating a new canvas must not abandon a staged Slimer layer."""
import ast
from pathlib import Path
from types import SimpleNamespace


def new_project_method():
    source = Path(__file__).resolve().parents[1].joinpath('friendly_animator.py').read_text()
    tree = ast.parse(source)
    method = next(n for cls in tree.body if isinstance(cls, ast.ClassDef) for n in cls.body
                  if isinstance(n, ast.FunctionDef) and n.name == 'new_project')
    namespace = {'QInputDialog': SimpleNamespace(getItem=lambda *args: (_ for _ in ()).throw(AssertionError('Dialog must not open')))}
    exec(compile(ast.Module(body=[method], type_ignores=[]), '<new_project>', 'exec'), namespace)
    return namespace['new_project']


def test_staged_slimer_layer_blocks_new_canvas_before_dialog():
    messages = []
    fake = SimpleNamespace(_slimer_pending_part=object(), status=SimpleNamespace(setText=messages.append))
    new_project_method()(fake)
    assert len(messages) == 1
    assert 'Apply Move' in messages[0]
    assert 'Cancel Unconfirmed Layer' in messages[0]
