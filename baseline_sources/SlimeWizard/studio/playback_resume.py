"""Decide where a non-looping preview should resume after reaching its end."""

def resume_position(elapsed_ms, durations, loop):
    """Restart a completed non-looping animation; otherwise preserve pause position."""
    position = max(0.0, float(elapsed_ms))
    total = sum(max(1, int(duration)) for duration in durations)
    if total <= 0:
        return 0.0
    if not loop and position >= total:
        return 0.0
    return position
