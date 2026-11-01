"""Regression checks for the provisional-layer cancel contract."""
from pathlib import Path


def test_cancel_is_available_and_uses_part_identity():
    source = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()
    start = source.index('    def slimer_cancel_editable_layer(self):')
    end = source.index('    def slimer_apply_move_to_pose(self):', start)
    implementation = source[start:end]
    assert 'part is pending' in implementation
    assert 'self.model.remove_unconfirmed_part(index)' in implementation
    assert '_slimer_erase_original_layers' not in implementation
    assert 'self.slimer_clear()' in implementation
    assert 'clicked.connect(self.slimer_cancel_editable_layer)' in source
