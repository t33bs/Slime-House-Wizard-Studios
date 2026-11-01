from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1].joinpath('friendly_animator.py').read_text()


def test_provisional_layer_tracks_asset_identity_not_only_row_number():
    create = SOURCE.split('def slimer_create_editable_layer(self):', 1)[1].split('def slimer_apply_move_to_pose(self):', 1)[0]
    apply = SOURCE.split('def slimer_apply_move_to_pose(self):', 1)[1].split('def _slimer_commit(', 1)[0]
    assert 'self._slimer_pending_part=self.model.parts[index]' in create
    assert 'if candidate is pending_part' in apply
    assert 'self._slimer_pending_part=None' in apply
