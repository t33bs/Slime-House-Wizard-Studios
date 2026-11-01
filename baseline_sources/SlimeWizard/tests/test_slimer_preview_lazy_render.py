"""Live selected-pixel preview is reused; canvas floating overlay stays transform-only."""
from pathlib import Path
SOURCE = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()

def test_live_preview_only_for_nonempty_mask():
    assert 'if self.slimer_selection.mask.getbbox() is not None:\n                confirmed_slimer_preview=self.slimer_preview()' in SOURCE

def test_slimer_preview_uses_clean_canvas_not_highlight_mask():
    assert 'confirmed_slimer_preview=self.slimer_preview()' in SOURCE
    assert 'pixmap(live_render, 132)' in SOURCE
    assert 'pixmap(confirmed_slimer_preview, 132)' not in SOURCE

def test_single_selection_mode_button():
    assert "self.slimer_finish=QPushButton" not in SOURCE
    assert '✓ Move Selection (finish highlighting)' in SOURCE
