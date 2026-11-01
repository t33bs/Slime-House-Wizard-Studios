"""Guard the staged-layer history ordering against visibility regressions."""
import ast
from pathlib import Path


def test_apply_move_records_history_after_staged_layer_visibility_is_restored():
    source = Path(__file__).resolve().parents[1] / 'friendly_animator.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    method = next(node for cls in tree.body if isinstance(cls, ast.ClassDef)
                  for node in cls.body if isinstance(node, ast.FunctionDef)
                  and node.name == 'slimer_apply_move_to_pose')
    restore = [node.lineno for node in ast.walk(method)
               if isinstance(node, ast.Assign) and any(
                   isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name)
                   and target.value.id == 'part' and isinstance(target.slice, ast.Constant)
                   and target.slice.value == 'visible' for target in node.targets)]
    remember = [node.lineno for node in ast.walk(method)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == 'remember']
    assert len(restore) >= 2 and len(remember) == 1
    assert max(restore) < remember[0], 'Undo history must not snapshot a hidden staged asset'
