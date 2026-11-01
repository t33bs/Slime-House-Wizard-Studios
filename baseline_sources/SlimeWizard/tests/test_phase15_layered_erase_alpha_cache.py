"""Layered Slimer provenance should not rerender layers already scanned."""
import ast
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1].joinpath('friendly_animator.py').read_text()

def test_ownership_alpha_is_reused_by_provenance_pass():
    method = SOURCE.split('    def _slimer_layered_erase_plan(self, mask):', 1)[1].split('    def _slimer_original_erase_safe(', 1)[0]
    assert 'rendered_alphas[i] = alpha' in method
    assert 'alpha = rendered_alphas.get(i)' in method
    assert 'if alpha is None:' in method
    ast.parse(SOURCE)
