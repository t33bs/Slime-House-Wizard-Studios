"""A hidden or nearly-zero-width dock must not conceal both previews."""
from pathlib import Path
SOURCE = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text(encoding='utf-8')

def test_restored_preview_dock_has_visible_minimum_width():
    assert 'max(235,int(saved[2]))' in SOURCE
    assert 'self.comparison_panel.setMinimumWidth(235)' in SOURCE
    assert 'self.comparison_panel.show()' in SOURCE

def test_rejected_destructive_move_returns_failure():
    start = SOURCE.index('    def _slimer_commit(self,as_frame,into_pose=False):')
    end = SOURCE.index('        # Commit the current pose BEFORE adding a new part.', start)
    block = SOURCE[start:end]
    assert 'self._slimer_original_erase_safe(selection.mask)' in block
    assert block.count('return False') >= 2
