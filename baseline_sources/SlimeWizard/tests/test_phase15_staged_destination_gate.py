"""The real Apply Move path must validate the staged layer before erasure."""
import ast
from pathlib import Path


def test_apply_move_checks_actual_staged_destination_before_source_erase():
    source = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()
    tree = ast.parse(source)
    method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'slimer_apply_move_to_pose')
    body = ast.get_source_segment(source, method)
    assert "self.model.render_part(index, self.model.resolved_pose()[index])" in body
    assert "destination.getchannel('A').getbbox() is None" in body
    assert body.index("destination.getchannel('A').getbbox() is None") < body.index("self._slimer_erase_original_layers(self._slimer_pending_mask)")
    assert "if not part.get('visible', True):" in body
