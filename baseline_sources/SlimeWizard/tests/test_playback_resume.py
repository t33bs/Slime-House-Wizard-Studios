from studio.playback_resume import resume_position


def test_completed_nonlooping_playback_restarts():
    assert resume_position(300, [100, 200], False) == 0
    assert resume_position(350, [100, 200], False) == 0


def test_paused_nonlooping_playback_resumes_position():
    assert resume_position(125, [100, 200], False) == 125


def test_looping_playback_keeps_elapsed_time():
    assert resume_position(350, [100, 200], True) == 350


def test_empty_animation_starts_at_zero():
    assert resume_position(200, [], False) == 0
