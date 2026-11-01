from studio.timeline_retime import retime_elapsed


def test_edit_current_pose_preserves_fractional_progress():
    assert retime_elapsed([100, 200, 100], 1, 200, 400) == 300


def test_edit_earlier_pose_shifts_later_playback():
    assert retime_elapsed([100, 200, 100], 0, 350, 200) == 450


def test_edit_later_pose_does_not_shift_earlier_playback():
    assert retime_elapsed([100, 200, 100], 2, 50, 500) == 50


def test_looped_playback_retimes_current_cycle():
    assert retime_elapsed([100, 100], 0, 250, 200) == 400


def test_invalid_index_is_safe():
    assert retime_elapsed([], 0, 30, 200) == 30
