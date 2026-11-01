"""Guard asset-list restoration against reentrant selection signals."""
import ast
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'friendly_animator.py'
TREE = ast.parse(SOURCE.read_text())

def method(name):
    return next(n for n in ast.walk(TREE) if isinstance(n, ast.FunctionDef) and n.name == name)

def test_history_asset_selector_restores_original_signal_state():
    body = ast.get_source_segment(SOURCE.read_text(), method('_after_history_change'))
    assert 'was_blocked = self.assets.blockSignals(True)' in body
    assert 'finally:' in body and 'self.assets.blockSignals(was_blocked)' in body
    assert body.index('self.assets.setCurrentRow(self.selected)') < body.index('self.assets.blockSignals(was_blocked)')

def test_project_asset_selector_restores_original_signal_state():
    body = ast.get_source_segment(SOURCE.read_text(), method('activate_project'))
    assert 'was_blocked = self.assets.blockSignals(True)' in body
    assert 'finally:' in body and 'self.assets.blockSignals(was_blocked)' in body
    assert body.index('self.assets.setCurrentRow(asset_row)') < body.index('self.assets.blockSignals(was_blocked)')
    assert 'self.selected = asset_row' in body
