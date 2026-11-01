"""Guard the empty-timeline transition against stale Slimer artwork."""
import ast
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'friendly_animator.py'

def test_deleting_last_pose_hides_overlay_and_resets_slimer():
    source = SOURCE.read_text()
    tree = ast.parse(source)
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'remove_pose')
    body = ast.get_source_segment(source, fn)
    assert "if frames:" in body and "else:" in body
    assert "part['visible'] = False" in body
    assert 'self._reset_slimer_for_project_change()' in body
    assert 'self._pose_draft_key = None' in body

def test_deleting_surviving_pose_loads_snapshot():
    source = SOURCE.read_text()
    tree = ast.parse(source)
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'remove_pose')
    body = ast.get_source_segment(source, fn)
    assert 'self.select_timeline_pose(min(self.frame, len(frames)-1))' in body
