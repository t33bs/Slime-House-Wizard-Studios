from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()


def test_move_original_preflight_checks_topmost_contributing_pixels_only():
    section = SOURCE.split('    def _slimer_original_erase_safe(self, mask=None):', 1)[1].split('    def _slimer_erase_original_layers(self, mask):', 1)[0]
    assert 'for i in range(len(states) - 1, -1, -1):' in section
    assert 'remaining = ImageChops.subtract(remaining, consumed)' in section
    assert 'if consumed.getbbox() is None:' in section
