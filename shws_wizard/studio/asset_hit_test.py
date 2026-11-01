"""Source-independent canvas asset selection: visible pixels, never padded PNG boxes."""


def choose_drag_layer(parts, selected, x, y, pixel_hit, *, staged=None):
    """Return the layer the user intends to drag, without mutating assets.

    A staged Slimer edit locks to its provisional destination until Apply or
    Cancel. With no pending edit, an explicitly selected visible layer gets
    first chance on its *actual* pixel footprint; otherwise use the topmost
    visible pixel. This prevents a later full-canvas Slimer PNG from stealing
    clicks on earlier layers (including when their visible pixels overlap).
    """
    def valid(index):
        return (0 <= index < len(parts) and
                parts[index].get('visible', True) and
                bool(pixel_hit(index, x, y)))

    if staged is not None:
        for index, part in enumerate(parts):
            if part is staged:
                return index if valid(index) else None
        return None  # A stale staged identity must never redirect to source.

    if valid(selected):
        return selected
    for index in range(len(parts) - 1, -1, -1):
        if valid(index):
            return index
    return None
