"""Guard timeline refresh and explicit selection against recursive Qt callbacks."""
import ast
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()
TREE = ast.parse(SOURCE)

def method_source(name):
    node = next(n for n in ast.walk(TREE) if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(SOURCE, node)

def test_refresh_timeline_restores_signal_state_after_row_selection():
    body = method_source('refresh_timeline')
    assert 'was_blocked = self.timeline.blockSignals(True)' in body
    assert 'finally:' in body and 'self.timeline.blockSignals(was_blocked)' in body
    assert body.index('self.timeline.setCurrentRow(self.frame)') < body.index('self.timeline.blockSignals(was_blocked)')

def test_explicit_timeline_selection_restores_signal_state():
    body = method_source('select_timeline_pose')
    assert 'was_blocked = self.timeline.blockSignals(True)' in body
    assert 'finally:' in body and 'self.timeline.blockSignals(was_blocked)' in body
    assert body.index('self.timeline.blockSignals(was_blocked)') < body.index('self.load_frame(index)')
