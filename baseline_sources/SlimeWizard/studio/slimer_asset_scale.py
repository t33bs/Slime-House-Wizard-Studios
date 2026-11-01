"""Non-destructive nearest-neighbor resize for Slimer's transparent full-canvas assets.

The imported Slimer layer is a canvas-sized PNG, but only the visible selected
pixels should grow or shrink.  Scaling the padded canvas itself would change
position and clip artwork without clearly communicating the operation.
"""
from PIL import Image


def scaled_selection_content(source, percent, pivot):
    """Return a new RGBA canvas with its visible pixels scaled about `pivot`.

    Recompute from a stable source at each percentage, rather than repeatedly
    resampling already-resized pixels. Refuse clipping instead of losing pixels.
    """
    image = source.convert('RGBA')
    if percent < 10 or percent > 800:
        raise ValueError('Resize percentage must be between 10% and 800%.')
    bounds = image.getchannel('A').getbbox()
    if bounds is None:
        raise ValueError('Cannot resize an empty asset.')
    if percent == 100:
        return image.copy()
    x0, y0, x1, y1 = bounds
    factor = percent / 100.0
    w = max(1, round((x1 - x0) * factor))
    h = max(1, round((y1 - y0) * factor))
    px, py = pivot
    left = round(px + (x0 - px) * factor)
    top = round(py + (y0 - py) * factor)
    if left < 0 or top < 0 or left + w > image.width or top + h > image.height:
        raise ValueError('Resized artwork would cross the canvas edge. Move it inward or use a smaller size.')
    crop = image.crop(bounds).resize((w, h), Image.Resampling.NEAREST)
    canvas = Image.new('RGBA', image.size)
    canvas.paste(crop, (left, top))
    return canvas
