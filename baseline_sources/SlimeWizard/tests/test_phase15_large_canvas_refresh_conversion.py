"""Editor refresh must convert the final composite only once per update."""
import ast
from pathlib import Path


def test_refresh_converts_final_composite_once_after_slimer_overlay():
    source = Path(__file__).resolve().parents[1].joinpath('friendly_animator.py').read_text()
    tree = ast.parse(source)
    method = next(node for cls in tree.body if isinstance(cls, ast.ClassDef)
                  for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == 'refresh')
    calls = [node for node in ast.walk(method) if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Name) and node.func.id == 'QImage']
    assert len(calls) == 1, 'Refresh must not build a discarded full-canvas QImage'
    body = ast.get_source_segment(source, method)
    assert body.index("if self.slimer_toggle.isChecked()") < body.index("rgba=composed.convert('RGBA')")
    assert body.index("rgba=composed.convert('RGBA')") < body.index('self.canvas.set_art(')
