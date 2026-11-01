"""Selector restoration must preserve caller signal-block state even on exceptions."""
import ast
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "friendly_animator.py"

def test_history_restore_preserves_previous_signal_state():
    tree = ast.parse(SOURCE.read_text())
    method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_after_history_restore")
    body = ast.get_source_segment(SOURCE.read_text(), method)
    assert "was_blocked = self.anim.blockSignals(True)" in body
    assert "finally:" in body and "self.anim.blockSignals(was_blocked)" in body

def test_project_switch_preserves_previous_signal_state():
    tree = ast.parse(SOURCE.read_text())
    method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and "self._project_animation[self._active_project_id]" in (ast.get_source_segment(SOURCE.read_text(), n) or ""))
    body = ast.get_source_segment(SOURCE.read_text(), method)
    assert "was_blocked = self.anim.blockSignals(True)" in body
    assert "finally:" in body and "self.anim.blockSignals(was_blocked)" in body
