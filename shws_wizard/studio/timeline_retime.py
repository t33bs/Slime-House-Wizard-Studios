"""Preserve playback position when a pose duration is edited live."""

def retime_elapsed(durations, frame_index, elapsed_ms, new_duration, loop=True):
    """Keep the fractional position within the edited pose, without rewinding others.

    Returns the adjusted elapsed time in milliseconds. Other pose boundaries stay
    fixed except for the shift caused by changing this pose's duration.
    """
    if not durations or not 0 <= frame_index < len(durations):
        return max(0.0, float(elapsed_ms))
    old = max(1, int(durations[frame_index]))
    new = max(1, int(new_duration))
    total = sum(max(1, int(d)) for d in durations)
    position = max(0.0, float(elapsed_ms))
    if loop and total:
        cycles, position = divmod(position, total)
    else:
        cycles = 0
        position = min(position, total)
    start = sum(max(1, int(d)) for d in durations[:frame_index])
    end = start + old
    if position < start:
        adjusted = position
    elif position < end:
        adjusted = start + (position - start) * new / old
    else:
        adjusted = position + new - old
    return cycles * (total - old + new) + adjusted
