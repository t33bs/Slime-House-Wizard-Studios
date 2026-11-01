"""Guard against history restoring a name absent from the selector."""
import ast
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "friendly_animator.py"

def test_history_restoration_inserts_missing_animation_before_selection():
    tree = ast.parse(SOURCE.read_text())
    method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_after_history_restore")
    body = ast.get_source_segment(SOURCE.read_text(), method)
    assert "self.anim.findText(animation) < 0" in body
    assert "self.anim.addItem(animation)" in body
    assert body.index("self.anim.addItem(animation)") < body.index("self.anim.setCurrentText(animation)")
    assert "finally:" in body and "self.anim.blockSignals(was_blocked)" in body
