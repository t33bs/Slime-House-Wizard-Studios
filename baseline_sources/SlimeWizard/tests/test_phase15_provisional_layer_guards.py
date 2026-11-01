"""Static regression contracts for uncommitted Slimer layer safety."""
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()


def test_uncommitted_layer_blocks_automatic_pose_save():
    body = SOURCE.split('    def preserve_pose_draft(self):', 1)[1].split('    def mark_pose_draft(self):', 1)[0]
    assert 'self._slimer_pending_layer is not None' in body
    assert 'if pending_slimer:return' in body


def test_uncommitted_layer_blocks_place_frame():
    body = SOURCE.split('    def slimer_place_frame(self):', 1)[1].split('    def remember(self):', 1)[0]
    assert 'if self._slimer_pending_layer is not None:' in body
    assert 'return False' in body
