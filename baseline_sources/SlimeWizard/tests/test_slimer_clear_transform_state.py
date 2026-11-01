from pathlib import Path


def test_clear_resets_floating_selection_and_drag_controls():
    source = (Path(__file__).resolve().parents[1] / "friendly_animator.py").read_text()
    method = source.split("    def slimer_clear(self):", 1)[1].split("    def _slimer_erase_original_layers", 1)[0]
    assert "self.canvas.slimer_transform_mode = False" in method
    assert "self.canvas.slimer_bounds = None" in method
    assert "self.canvas._slimer_handle = None" in method
    assert "self.slimer_drag_toggle.setChecked(False)" in method
    assert "self.slimer_phase_masks={}" in method
