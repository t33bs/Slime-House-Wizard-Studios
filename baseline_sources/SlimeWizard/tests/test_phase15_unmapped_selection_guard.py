from pathlib import Path


def test_preflight_rejects_unmapped_selected_pixels():
    source = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()
    preflight = source.split('    def _slimer_original_erase_safe(self, mask=None):', 1)[1].split('    def _slimer_erase_original_layers(self, mask):', 1)[0]
    assert 'if remaining is not None and remaining.getbbox() is not None:' in preflight
    assert 'return False' in preflight.split('if remaining is not None and remaining.getbbox() is not None:', 1)[1]
