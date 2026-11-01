"""Source-level checks for selection/canvas alignment after history restore."""
import ast
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'friendly_animator.py'

def test_history_restores_pose_identity_and_loads_canvas():
    module = ast.parse(SOURCE.read_text())
    methods = {node.name: node for cls in module.body if isinstance(cls, ast.ClassDef)
               for node in cls.body if isinstance(node, ast.FunctionDef)}
    restore = ast.unparse(methods['_after_history_restore'])
    assert 'ids.index(pose_id)' in restore
    assert 'self.select_timeline_pose(index)' in restore
    assert 'self._timeline_structure_changed()' in restore
    for action in ('undo', 'redo'):
        source = ast.unparse(methods[action])
        assert 'self._history_selection()' in source
        assert 'self._after_history_restore(previous_timeline, selection)' in source
