"""A missing provisional layer must never leave Slimer transaction-locked."""
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()


def test_cancel_missing_pending_releases_lock_and_resets_selection():
    start = SOURCE.index('    def slimer_cancel_editable_layer(self):')
    end = SOURCE.index('    def slimer_apply_move_to_pose(self):', start)
    method = SOURCE[start:end]
    missing = method[method.index('        if index is None:'):method.index('        self.remember()', method.index('        if index is None:'))]
    assert 'self.model.parts.pop' not in missing
    for name in ('_slimer_pending_layer', '_slimer_pending_part', '_slimer_pending_source', '_slimer_pending_mask', '_slimer_pending_move_original'):
        assert f'self.{name} = None' in missing
    assert 'self.slimer_move_original.setEnabled(True)' in missing
    assert 'self.slimer_clear()' in missing


def test_apply_missing_pending_uses_safe_cancel_not_stale_index():
    start = SOURCE.index('    def slimer_apply_move_to_pose(self):')
    end = SOURCE.index('    def _slimer_commit(', start)
    method = SOURCE[start:end]
    assert 'if pending_part is not None:' in method
    assert 'self.slimer_cancel_editable_layer()' in method
