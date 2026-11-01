from pathlib import Path
SOURCE = Path(__file__).resolve().parents[1].joinpath('friendly_animator.py').read_text()

def test_live_preview_during_highlighting():
    assert 'confirmed_slimer_preview=self.slimer_preview()' in SOURCE
    assert 'confirmed_slimer_preview=self.slimer_preview()' in SOURCE
    assert "pixmap(live_render, 132)" in SOURCE

def test_floating_result_only_drawn_during_transform():
    assert 'if self.canvas.slimer_transform_mode:\n                preview=confirmed_slimer_preview' in SOURCE
    assert 'composed.alpha_composite(preview)' in SOURCE
    assert 'if not self.canvas.slimer_transform_mode:' in SOURCE
    assert 'composed.alpha_composite(tint)' in SOURCE
    assert 'composed=live_render.copy()' in SOURCE
