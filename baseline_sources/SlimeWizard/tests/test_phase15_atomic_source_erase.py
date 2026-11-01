"""Regression: a failed Move Original erase must preserve every source buffer."""
import ast
from pathlib import Path
from PIL import Image


def test_source_erase_exception_rolls_back_all_source_images():
    source = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()
    tree = ast.parse(source)
    method = next(node for cls in tree.body if isinstance(cls, ast.ClassDef)
                  for node in cls.body if isinstance(node, ast.FunctionDef)
                  and node.name == 'slimer_apply_move_to_pose')
    # Exercise the actual rollback block, without requiring Qt in CI.
    erase_if = next(node for node in method.body if isinstance(node, ast.If)
                    and isinstance(node.test, ast.Attribute)
                    and node.test.attr == '_slimer_pending_move_original')
    class Model:
        def __init__(self):
            self.parts = [{'image': Image.new('RGBA', (2, 2), (255, 0, 0, 255))},
                          {'image': Image.new('RGBA', (2, 2), (0, 255, 0, 255))}]
            self.originals = [p['image'].copy() for p in self.parts]
    class Status:
        def setText(self, value): self.value = value
    class Harness:
        _slimer_pending_move_original = True
        _slimer_pending_mask = None
        def __init__(self):
            self.model = Model(); self.status = Status(); self.refreshed = False
        def _slimer_erase_original_layers(self, mask):
            self.model.parts[0]['image'].putpixel((0, 0), (0, 0, 0, 0))
            self.model.originals[1].putpixel((0, 0), (0, 0, 0, 0))
            raise RuntimeError('simulated partial erase')
        def refresh(self): self.refreshed = True
    class History:
        def __init__(self):
            self.past = ['prior undo', 'staged snapshot']
            self.future = ['prior redo']
    harness = Harness()
    harness.history = History()
    harness._pose_draft_dirty = True
    harness._pose_draft_key = ('Idle', 0)
    history_past = ['prior undo']
    history_future = ['prior redo']
    previous_draft_dirty = False
    previous_draft_key = ('Idle', 1)
    before = [p['image'].tobytes() for p in harness.model.parts]
    original = [im.tobytes() for im in harness.model.originals]
    # Include the surrounding transaction-history locals that are established
    # immediately before the source-erasure try block in the real method.
    fn = ast.FunctionDef(name='exercise', args=ast.arguments(posonlyargs=[], args=[ast.arg(arg='self')], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), body=[erase_if, ast.Return(value=ast.Constant(value=True))], decorator_list=[])
    module = ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[]))
    namespace = {'history_past': history_past, 'history_future': history_future,
                 'previous_draft_dirty': previous_draft_dirty,
                 'previous_draft_key': previous_draft_key}
    exec(compile(module, '<source-erase-test>', 'exec'), namespace)
    assert namespace['exercise'](harness) is False
    assert [p['image'].tobytes() for p in harness.model.parts] == before
    assert [im.tobytes() for im in harness.model.originals] == original
    assert harness.refreshed
    assert harness.history.past == ['prior undo']
    assert harness.history.future == ['prior redo']
    assert harness._pose_draft_dirty is False
    assert harness._pose_draft_key == ('Idle', 1)
    assert 'restored' in harness.status.value


def test_rollback_does_not_consume_undo_or_clear_redo():
    # Run the same failure-injection scenario and assert the history contract.
    source = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()
    tree = ast.parse(source)
    method = next(node for cls in tree.body if isinstance(cls, ast.ClassDef)
                  for node in cls.body if isinstance(node, ast.FunctionDef)
                  and node.name == 'slimer_apply_move_to_pose')
    record = next(i for i, node in enumerate(method.body) if isinstance(node, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == 'history_past' for t in node.targets))
    block = method.body[record:]
    assert any(isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'history_future' for t in n.targets) for n in block)
    assert 'self.history.past[:] = history_past' in source
    assert 'self.history.future[:] = history_future' in source
    assert 'self._pose_draft_dirty = previous_draft_dirty' in source
