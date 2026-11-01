from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1].joinpath("friendly_animator.py").read_text()

def test_provisional_layer_locks_copy_move_policy_until_confirmation():
    create = SOURCE.split("def slimer_create_editable_layer(self):", 1)[1].split("def slimer_apply_move_to_pose(self):", 1)[0]
    apply = SOURCE.split("def slimer_apply_move_to_pose(self):", 1)[1].split("def _slimer_commit(", 1)[0]
    assert "self._slimer_pending_move_original=self.slimer_move_original.isChecked()" in create
    assert "self.slimer_move_original.setEnabled(False)" in create
    assert "self.slimer_move_original.setEnabled(True)" in apply
    assert "self._slimer_pending_move_original=None" in apply
