"""Pure geometry for viewport-safe on-canvas transform handles (no Qt)."""


def visible_handle_position(desired, corners, width, height, blocked=None, margin=22, padding=64):
    """Return reachable screen pixels for an X/Y/R handle, or None if offscreen.

    `desired` is the natural screen position of a control; `corners` enclose
    the selected *artwork*, not a full-canvas transparent PNG. The selection
    must intersect the widget. Handles are tethered to the visible part of
    the artwork when high zoom cuts their natural position offscreen.
    `blocked` is an optional rectangle occupied by the floating canvas menu.
    """
    if width <= 2 * margin or height <= 2 * margin or not corners:
        return None
    xs, ys = zip(*corners)
    left, right = min(xs), max(xs)
    top, bottom = min(ys), max(ys)
    if right < 0 or left > width or bottom < 0 or top > height:
        return None
    # Preserve the old, intuitive position whenever it is actually reachable.
    # In particular, existing assets may have artist-defined rotation pivots
    # away from the opaque footprint; do not nudge those healthy controls.
    menu_covering = (blocked is not None and
                     blocked[0] - 12 <= desired[0] <= blocked[2] + 12 and
                     blocked[1] - 12 <= desired[1] <= blocked[3] + 12)
    if (margin <= desired[0] <= width - margin and
            margin <= desired[1] <= height - margin and not menu_covering):
        return desired
    min_x = max(margin, left - padding)
    max_x = min(width - margin, right + padding)
    min_y = max(margin, top - padding)
    max_y = min(height - margin, bottom + padding)
    if min_x > max_x or min_y > max_y:
        # A tiny sliver of artwork at the edge still gets a reachable control.
        min_x, max_x = margin, width - margin
        min_y, max_y = margin, height - margin
    clamp = lambda value, lo, hi: min(max(value, lo), hi)
    x = clamp(desired[0], min_x, max_x)
    y = clamp(desired[1], min_y, max_y)
    if blocked is not None:
        bx0, by0, bx1, by1 = blocked
        # Make room for a 20px handle, not just the cursor center.
        bx0, by0, bx1, by1 = bx0 - 12, by0 - 12, bx1 + 12, by1 + 12
        if bx0 <= x <= bx1 and by0 <= y <= by1:
            candidates = [(clamp(bx0 - 1, min_x, max_x), y),
                          (x, clamp(by1 + 1, min_y, max_y)),
                          (x, clamp(by0 - 1, min_y, max_y)),
                          (clamp(bx1 + 1, min_x, max_x), y)]
            allowed = [(a, b) for a, b in candidates
                       if not (bx0 <= a <= bx1 and by0 <= b <= by1)]
            if allowed:
                x, y = min(allowed, key=lambda point:
                           (point[0] - x) ** 2 + (point[1] - y) ** 2)
            else:
                # A huge menu can cover the entire visible selection. Keep
                # the handle reachable in the widget before returning None.
                backups = [(margin, y), (width - margin, y),
                           (x, margin), (x, height - margin)]
                allowed = [(a, b) for a, b in backups
                           if not (bx0 <= a <= bx1 and by0 <= b <= by1)]
                if not allowed:
                    return None
                x, y = min(allowed, key=lambda point:
                           (point[0] - x) ** 2 + (point[1] - y) ** 2)
    return x, y
