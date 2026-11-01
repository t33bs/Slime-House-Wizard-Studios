from pathlib import Path


def test_apply_requires_staged_object_identity_not_only_row():
    source = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()
    method = source.split('    def slimer_apply_move_to_pose(self):', 1)[1].split('    def _slimer_commit(', 1)[0]
    assert 'if pending_part is None:' in method
    assert 'No verified staged Slimer layer' in method
    assert 'if candidate is pending_part' in method
    assert method.index('if pending_part is None:') < method.index('if not 0 <= index')
