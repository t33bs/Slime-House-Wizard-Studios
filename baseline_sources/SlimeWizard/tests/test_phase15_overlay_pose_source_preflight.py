"""Static safety gate for repeated edits on restored Slimer overlay sources."""
import ast
from pathlib import Path


def test_overlay_pose_source_is_used_for_erase_and_preflight():
    source = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()
    tree = ast.parse(source)
    methods = {node.name: ast.get_source_segment(source, node) for node in ast.walk(tree)
               if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    preflight = methods['_slimer_original_erase_safe']
    erase = methods['_slimer_erase_original_layers']
    assert "part.get('name') == 'Slimer pose overlay'" in preflight
    assert "source.tobytes() == self.model.originals[i].tobytes()" in preflight
    assert "state.get('source_png')" in erase
    assert "self.model._decode_source(state['source_png'])" in erase
