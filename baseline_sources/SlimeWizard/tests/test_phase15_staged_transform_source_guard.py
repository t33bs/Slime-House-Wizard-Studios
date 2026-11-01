"""Source-contract regression for non-table transforms while Slimer stages a layer."""
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()


def test_non_table_transforms_protect_staged_source():
    for method in ('flip_selected', 'center_selected', 'reset_size'):
        start = SOURCE.index('    def ' + method + '(')
        end = SOURCE.find('\n    def ', start + 5)
        body = SOURCE[start:end if end != -1 else None]
        assert '_slimer_protect_staged_source' in body
        assert body.index('_slimer_protect_staged_source') < body.index('self.remember()')


def test_guard_allows_destination_and_refuses_other_assets():
    start = SOURCE.index('    def _slimer_protect_staged_source(')
    end = SOURCE.index('\n    def ', start + 5)
    body = SOURCE[start:end]
    assert 'self.model.parts[self.selected] is not pending' in body
    assert 'return False' in body
    assert 'return True' in body
