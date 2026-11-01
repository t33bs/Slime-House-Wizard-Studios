"""Timing for previewing saved creature poses; no external reference content."""


def frame_at_time(durations, elapsed_ms, repeat=True):
    durations = [max(1, int(d)) for d in durations]
    if not durations:
        return None
    total = sum(durations)
    elapsed = max(0.0, float(elapsed_ms))
    cursor = elapsed % total if repeat else min(elapsed, max(0.0, total - 1e-6))
    for index, duration in enumerate(durations):
        if cursor < duration:
            return index
        cursor -= duration
    return len(durations) - 1
