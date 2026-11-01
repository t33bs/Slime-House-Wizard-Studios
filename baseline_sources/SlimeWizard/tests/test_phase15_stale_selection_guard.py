"""Regression contract: do not destructively commit a stale Slimer selection."""
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text(encoding='utf-8')


def test_stale_source_is_rejected_before_undo_snapshot_and_erase():
    start = SOURCE.index('    def _slimer_commit(self,as_frame,into_pose=False):')
    end = SOURCE.index('    def slimer_place_layer(self):', start)
    body = SOURCE[start:end]
    assert 'selection.source.tobytes() != self.model.render().tobytes()' in body
    assert body.index('selection.source.tobytes()') < body.index('self.remember()')
    assert 'Selection source is stale' in body
    assert 'return False' in body
