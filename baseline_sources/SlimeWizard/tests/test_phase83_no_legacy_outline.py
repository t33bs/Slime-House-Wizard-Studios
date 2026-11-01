"""Paint highlight tint remains visible without a misleading transform outline."""
import ast
from pathlib import Path

def test_highlight_outline_only_exists_in_transform_mode():
    text = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()
    tree=ast.parse(text)
    canvas=next(c for c in tree.body if isinstance(c,ast.ClassDef) and c.name=='DragCanvas')
    paint=next(m for m in canvas.body if isinstance(m,ast.FunctionDef) and m.name=='paintEvent')
    source=ast.get_source_segment(text,paint)
    assert 'if self.slimer_active and self.slimer_transform_mode and self.slimer_bounds is not None:' in source
    assert 'self.asset_controls_enabled and not self.slimer_active' in source
