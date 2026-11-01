"""Exact nearest-neighbor provenance for the current PIL part renderer.

This is a read-only mapping utility. It deliberately does not authorize
Slimer's destructive Move Original operation on rotated/resized layers.
"""
from PIL import Image
from array import array


def rendered_source_indices(source_size, canvas_size, x, y, width, height,
                            angle=0, anchor=None):
    """Map each rendered canvas pixel to its original source pixel index.

    Values are -1 for empty pixels. All resize/rotate operations use the
    same Pillow nearest-neighbor operations and order as render_part().
    """
    sw, sh = map(int, source_size)
    cw, ch = map(int, canvas_size)
    width, height = int(width), int(height)
    if min(sw, sh, cw, ch, width, height) < 1:
        raise ValueError('Source, canvas and rendered dimensions must be positive.')
    if anchor is None:
        anchor = (width // 2, height // 2)
    # Reserve zero for transparent/off-canvas; source indices are 1-based.
    # Build the provenance labels in a compact contiguous integer buffer.
    # putdata(list(range(...))) creates over a million Python integers for a
    # 1024x1024 source, wasting memory and delaying each Slimer preflight.
    indices = array('i', range(1, sw * sh + 1))
    labels = Image.frombytes('I', (sw, sh), indices.tobytes())
    scaled = labels.resize((width, height), Image.Resampling.NEAREST)
    canvas = Image.new('I', (cw, ch), 0)
    canvas.paste(scaled, (int(x), int(y)))
    if float(angle) % 360:
        canvas = canvas.rotate(float(angle), Image.Resampling.NEAREST,
                               center=(int(x) + anchor[0], int(y) + anchor[1]),
                               expand=False)
    return canvas


def selected_source_indices(mapping, selection_mask):
    """Return unique source indices touched by a canvas selection."""
    if mapping.size != selection_mask.size:
        raise ValueError('Selection and mapping must share canvas dimensions.')
    return {label - 1 for label, selected in zip(mapping.get_flattened_data(), selection_mask.get_flattened_data())
            if selected and label > 0}


def classify_source_selection(mapping, selection_mask, visible_alpha=None):
    """Separate fully selected source pixels from partially selected ones.

    A source pixel may generate several canvas pixels after nearest-neighbor
    scaling/rotation. Only when *all visible occurrences* are selected can
    erasing the source be lossless with respect to unselected rendered pixels.
    Transparent rendered occurrences are excluded when visible_alpha is given.
    Returns (complete_indices, partial_indices).
    """
    if mapping.size != selection_mask.size:
        raise ValueError('Selection and mapping must share canvas dimensions.')
    if visible_alpha is not None and visible_alpha.size != mapping.size:
        raise ValueError('Alpha and mapping must share canvas dimensions.')
    seen, selected = set(), set()
    labels = mapping.get_flattened_data()
    masks = selection_mask.get_flattened_data()
    alphas = visible_alpha.get_flattened_data() if visible_alpha is not None else None
    for n, (label, marked) in enumerate(zip(labels, masks)):
        if label <= 0 or (alphas is not None and not alphas[n]):
            continue
        index = label - 1
        seen.add(index)
        if marked:
            selected.add(index)
    unselected = set()
    for n, (label, marked) in enumerate(zip(labels, masks)):
        if label > 0 and not marked and (alphas is None or alphas[n]):
            unselected.add(label - 1)
    return selected - unselected, selected & unselected


def classify_topmost_source_selection(layers, selection_mask):
    """Classify selection footprints by visible topmost contributing layer.

    layers are bottom-to-top (source-index mapping, rendered alpha) pairs.
    Pixels hidden by a higher nontransparent layer do not count as exposed
    occurrences of a lower source pixel. This is read-only; partial-alpha
    compositing and destructive editing still require separate safeguards.
    Returns one (complete, partial) pair per layer.
    """
    size = selection_mask.size
    if any(mapping.size != size or alpha.size != size for mapping, alpha in layers):
        raise ValueError('All layer mappings and alpha masks must match selection dimensions.')
    owners = [-1] * (size[0] * size[1])
    mappings = [list(mapping.get_flattened_data()) for mapping, _ in layers]
    alphas = [list(alpha.get_flattened_data()) for _, alpha in layers]
    for i, (labels, alpha) in enumerate(zip(mappings, alphas)):
        for j, (label, a) in enumerate(zip(labels, alpha)):
            if label > 0 and a:
                owners[j] = i
    marks = list(selection_mask.get_flattened_data())
    result = []
    for i, labels in enumerate(mappings):
        chosen, omitted = set(), set()
        for j, label in enumerate(labels):
            if owners[j] != i or label <= 0:
                continue
            (chosen if marks[j] else omitted).add(label - 1)
        result.append((chosen - omitted, chosen & omitted))
    return result


def classify_contributing_source_selection(layers, selection_mask):
    """Conservative footprint classification for alpha-composited layers.

    A source occurrence contributes if its rendered alpha is nonzero and no
    *fully opaque* higher layer covers it. Partial-alpha layers do not hide
    lower contributions. All contributing occurrences must be selected before
    a source pixel is classified complete. This is read-only and does not
    authorize destructive editing.
    """
    size = selection_mask.size
    if any(mapping.size != size or alpha.size != size for mapping, alpha in layers):
        raise ValueError('All layer mappings and alpha masks must match selection dimensions.')
    # A canvas may contain 1024x1024 pixels. Avoid expanding each layer's
    # integer provenance labels and 8-bit masks into millions of Python ints.
    # Mode I is a native signed 32-bit buffer; L is a one-byte mask.
    marks = memoryview(selection_mask.convert('L').tobytes())
    covered = bytearray(len(marks))
    result = [None] * len(layers)
    for i in range(len(layers) - 1, -1, -1):
        mapping, alpha = layers[i]
        labels = memoryview(mapping.convert('I').tobytes()).cast('i')
        alphas = memoryview(alpha.convert('L').tobytes())
        chosen, omitted = set(), set()
        for j, (label, a) in enumerate(zip(labels, alphas)):
            if label > 0 and a > 0 and not covered[j]:
                (chosen if marks[j] else omitted).add(label - 1)
            if a == 255:
                covered[j] = 1
        result[i] = (chosen - omitted, chosen & omitted)
    return result


def plan_complete_source_erase(mapping, rendered_alpha, selection_mask):
    """Plan source indices for a lossless single-layer destructive move.

    Return None if any selected source pixel has an unselected visible
    occurrence. An empty set means the selection touches no visible source.
    This is a preflight plan, not a mutation or multi-layer authorization.
    """
    complete, partial = classify_source_selection(mapping, selection_mask, rendered_alpha)
    return None if partial else complete


def erase_planned_source_pixels(source, source_indices):
    """Return a new RGBA image with planned source pixels cleared.

    Never mutate the caller's source; reject invalid indices before editing.
    The caller must first establish that the plan covers complete visible
    footprints and that the source matches the rendered pose.
    """
    result = source.convert('RGBA').copy()
    indices = set(source_indices)
    if any(not isinstance(i, int) or i < 0 or i >= result.width * result.height
           for i in indices):
        raise ValueError('Source pixel index outside image bounds.')
    pixels = list(result.get_flattened_data())
    for i in indices:
        pixels[i] = (0, 0, 0, 0)
    result.putdata(pixels)
    return result
