import ast
from pathlib import Path


def test_history_resets_stale_slimer_and_syncs_animation_before_pose():
    tree = ast.parse((Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text())
    methods = {node.name: node for cls in tree.body if isinstance(cls, ast.ClassDef)
               for node in cls.body if isinstance(node, ast.FunctionDef)}
    source = ast.unparse(methods['_after_history_restore'])
    assert 'self._reset_slimer_for_project_change()' in source
    assert 'self.anim.setCurrentText(animation)' in source
    assert source.index('self.anim.setCurrentText(animation)') < source.index('self.select_timeline_pose(index)')
    assert 'if animation != previous_animation:' in source
