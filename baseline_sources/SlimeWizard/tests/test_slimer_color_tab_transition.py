"""Static regression for tab-specific Slimer transform state."""
import ast
from pathlib import Path

def test_color_tab_switch_clears_old_transform_handles():
    tree=ast.parse((Path(__file__).resolve().parents[1]/"friendly_animator.py").read_text())
    methods={n.name:n for c in tree.body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef)}
    code=ast.unparse(methods["slimer_switch_phase"])
    for item in ("self.canvas.slimer_transform_mode = False", "self.canvas.slimer_bounds = None", "self.canvas._slimer_handle = None", "self.slimer_drag_toggle.setChecked(False)", "self._slimer_mouse_transforming = False"):
        assert item in code
    assert code.index("self.slimer_phase_masks[previous]") < code.index("self.canvas.slimer_transform_mode = False")
    assert code.index("self.canvas.slimer_transform_mode = False") < code.index("self.slimer_selection.mask = self.slimer_phase_masks.get")
