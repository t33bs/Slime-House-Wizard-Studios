"""An unconfirmed editable layer must not have Undo swallowed by Slimer brush history."""
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()


def test_pending_layer_history_precedes_selection_history():
    undo = SOURCE.split('    def undo(self):', 1)[1].split('    def redo(self):', 1)[0]
    redo = SOURCE.split('    def redo(self):', 1)[1].split('    def _set_asset_visibility_in_current_pose', 1)[0]
    for body in (undo, redo):
        assert "getattr(self, '_slimer_pending_part', None) is None" in body
        assert 'self.history.' in body
        assert 'self._after_history_restore' in body
