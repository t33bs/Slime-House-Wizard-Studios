"""Regression: removed reference viewer, real frame preview timing unaffected."""
from studio.preview_timing import frame_at_time


def test_preview_frame_timing_and_loop():
    assert frame_at_time([100,300,100], 0) == 0
    assert frame_at_time([100,300,100], 150) == 1
    assert frame_at_time([100,300,100], 450) == 2
    assert frame_at_time([100,200],350) == 0
    assert frame_at_time([100,200],999,False) == 1
    assert frame_at_time([],0) is None

def test_reference_only_feature_is_not_importable():
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    assert not (root/'studio'/'user_reference.py').exists()
    assert not (root/'studio'/'comparison_sync.py').exists()
