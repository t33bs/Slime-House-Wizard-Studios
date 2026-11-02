"""Slime Cleaner: erase the uppermost visible pixel from any editable layer.

The plain, unrotated API is kept compatible with earlier callers.  The GUI
passes resolved per-pose states so a Slimer/Combined Artwork layer can be
cleaned just like the original PNG, even after a pose-specific transformation.
"""
from PIL import Image


def _rotated_source_lookup(part, state, canvas_size):
    """Use the renderer's exact NEAREST rotation to map canvas pixels to source.

    Inverse floating-point rounding can erase a neighboring pixel around a
    rotated edge. Instead, render a unique source-pixel ID with the same
    nearest-neighbor transform as PetSuiteModel.render_part(). The ID map is
    ephemeral and never appears in art or exports.
    """
    source = part['image']
    w, h = source.size
    if w * h >= 0xFFFFFF:
        raise ValueError('Cleaner cannot identify pixels on a layer this large safely.')
    ids = Image.new('RGBA', source.size)
    source_pixels = source.load()
    id_pixels = ids.load()
    for py in range(h):
        for px in range(w):
            if source_pixels[px, py][3]:
                identifier = py * w + px + 1
                id_pixels[px, py] = (identifier & 255,
                                     (identifier >> 8) & 255,
                                     (identifier >> 16) & 255, 255)
    full = Image.new('RGBA', tuple(canvas_size))
    x, y = int(state['x']), int(state['y'])
    full.paste(ids, (x, y))
    angle = float(state.get('angle', 0))
    if angle % 360:
        # The model applies rotation around this joint, or the center by default.
        ax, ay = state.get('_cleaner_anchor', (w // 2, h // 2))
        full = full.rotate(angle, Image.Resampling.NEAREST,
                           center=(x + ax, y + ay), expand=False)
    return full


def erase_visible_pixels(parts, x, y, brush_size=1, *, states=None,
                         canvas_size=None, modified_indices=None,
                         before_first_change=None):
    """Erase only the topmost *visible* source pixel at each brush coordinate.

    Hidden and lower-layer pixels remain intact, even when multiple layers
    overlap. ``states`` may include resolved x/y/angle/_cleaner_anchor from the
    active pose. ``modified_indices`` records changed source indices.
    ``before_first_change`` runs exactly once just before the first mutation,
    letting callers create a single Undo record without saving empty strokes.
    """
    size = max(1, int(brush_size))
    start = -(size // 2)
    changed = False
    states = states if states is not None else parts
    lookup = {}
    for cy in range(int(y) + start, int(y) + start + size):
        for cx in range(int(x) + start, int(x) + start + size):
            if canvas_size is not None and not (0 <= cx < canvas_size[0] and 0 <= cy < canvas_size[1]):
                continue
            for index in range(min(len(parts), len(states))-1, -1, -1):
                part, state = parts[index], states[index]
                if not state.get('visible', part.get('visible', True)):
                    continue
                image = part['image']
                if image.mode != 'RGBA':
                    image = image.convert('RGBA').copy()
                    part['image'] = image
                angle = float(state.get('angle', 0))
                if angle % 360:
                    if canvas_size is None:
                        # Without a canvas size there is no safe coordinate
                        # inverse. Refuse instead of guessing which pixel.
                        continue
                    if index not in lookup:
                        lookup[index] = _rotated_source_lookup(part, state, canvas_size)
                    rgba = lookup[index].getpixel((cx, cy))
                    if rgba[3] == 0:
                        continue
                    identifier = rgba[0] | (rgba[1] << 8) | (rgba[2] << 16)
                    if identifier == 0:
                        continue
                    source_index = identifier - 1
                    px, py = source_index % image.width, source_index // image.width
                else:
                    px = cx - int(state.get('x', 0))
                    py = cy - int(state.get('y', 0))
                if not (0 <= px < image.width and 0 <= py < image.height):
                    continue
                if image.getpixel((px, py))[3] == 0:
                    continue
                if not changed and before_first_change is not None:
                    before_first_change()
                image.putpixel((px, py), (0, 0, 0, 0))
                changed = True
                if modified_indices is not None:
                    modified_indices.add(index)
                break
    return changed
