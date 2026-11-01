"""Regression test for color-tab selection persistence without Qt dependency."""
import ast
from pathlib import Path
from types import SimpleNamespace
from PIL import Image

SOURCE = Path(__file__).resolve().parents[1] / 'friendly_animator.py'

class Spin:
    def __init__(self, value): self._value = value
    def value(self): return self._value
    def setValue(self, value): self._value = value
    def blockSignals(self, enabled): pass


def test_color_tab_switch_restores_independent_history_and_transforms():
    tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and any(isinstance(n, ast.FunctionDef) and n.name == 'slimer_switch_phase' for n in node.body))
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'slimer_switch_phase')
    from studio.signal_guard import blocked_signals
    namespace = {'Image': Image, 'blocked_signals': blocked_signals}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(SOURCE), 'exec'), namespace)
    obj = SimpleNamespace(
        slimer_selection=SimpleNamespace(mask=Image.new('L', (8, 8))),
        slimer_phase_masks={}, slimer_phase_transforms={}, slimer_phase_histories={},
        _slimer_current_phase='Start', slimer_selection_undo=['start-edit'],
        slimer_selection_redo=['start-redo'], model=SimpleNamespace(size=(8, 8)),
        slimer_dx=Spin(3), slimer_dy=Spin(4), slimer_turn=Spin(15), slimer_scale=Spin(125),
        _slimer_sync_numeric_values=lambda: None,
        _update_slimer_color_button=lambda: None, refresh=lambda: None,
    )
    obj.slimer_selection.mask.putpixel((2, 2), 255)
    namespace['slimer_switch_phase'](obj, 'Middle')
    assert obj.slimer_selection.mask.getbbox() is None
    assert (obj.slimer_dx.value(), obj.slimer_scale.value()) == (0, 100)
    obj.slimer_selection.mask.putpixel((5, 5), 255)
    obj.slimer_selection_undo.append('middle-edit')
    obj.slimer_dx.setValue(9)
    namespace['slimer_switch_phase'](obj, 'Start')
    assert obj.slimer_selection.mask.getpixel((2, 2)) == 255
    assert obj.slimer_selection.mask.getpixel((5, 5)) == 0
    assert obj.slimer_selection_undo == ['start-edit']
    assert obj.slimer_selection_redo == ['start-redo']
    assert (obj.slimer_dx.value(), obj.slimer_dy.value(), obj.slimer_turn.value(), obj.slimer_scale.value()) == (3, 4, 15, 125)
    namespace['slimer_switch_phase'](obj, 'Middle')
    assert obj.slimer_selection_undo == ['middle-edit']
    assert obj.slimer_selection.mask.getpixel((5, 5)) == 255
    assert obj.slimer_dx.value() == 9
