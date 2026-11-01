"""Prevent reentrant step-selection while rebuilding animation controls."""
import ast
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'friendly_animator.py'

def test_animation_switch_blocks_step_signals_during_rebuild():
    tree = ast.parse(SOURCE.read_text())
    method = next(node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == 'change_anim')
    body = ast.get_source_segment(SOURCE.read_text(), method)
    assert 'self.steps' not in body
    assert body.index('self.model.current=name') < body.index('self.select_step(0)')

def test_animation_switch_explicitly_loads_saved_pose_and_clears_empty_draft():
    tree = ast.parse(SOURCE.read_text())
    method = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == 'change_anim')
    body = ast.get_source_segment(SOURCE.read_text(), method)
    assert 'if poses:' in body and 'self.select_step(0)' in body
    assert 'self._pose_draft_key=None' in body
    assert body.index('self.select_step(0)') < body.index('self._reset_slimer_for_project_change()')
