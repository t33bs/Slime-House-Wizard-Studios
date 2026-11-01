"""Check whether a transformed Slimer destination would discard artwork."""
from PIL import Image


def destination_fits_canvas(image, x, y, angle, anchor, canvas_size):
    """Check all nontransparent nearest-neighbor destination pixels, including rotated ones.

    Rotate on a padded local surface so the canvas cannot clip artwork before
    the bounds check. This uses the same Pillow rotation center and sampling
    as PetSuiteModel.render_part.
    """
    # The staged asset is already RGBA. Avoid a full-size duplicate before
    # examining its alpha, especially for 1024x1024 Slimer selections.
    alpha = image.getchannel('A') if image.mode == 'RGBA' else image.convert('RGBA').getchannel('A')
    if alpha.getbbox() is None:
        return False
    w, h = image.size
    # PetSuiteModel.render_part pastes the asset onto a canvas BEFORE it
    # rotates that canvas. Pixels outside the initial canvas are discarded
    # even if the subsequent rotation would bring them back into view.
    # Check the pre-rotation footprint too, or Move Original could erase
    # source pixels that the actual renderer never displays.
    rotated = float(angle) % 360 != 0
    if rotated:
        left, top, right, bottom = alpha.getbbox()
        width, height = canvas_size
        if (int(x) + left < 0 or int(y) + top < 0
                or int(x) + right > width or int(y) + bottom > height):
            return False
    if rotated:
        # Rotate only the occupied alpha rectangle. Transparent margins of a
        # full-canvas staged layer should not force a huge rotation surface.
        left, top, right, bottom = alpha.getbbox()
        occupied = alpha.crop((left, top, right, bottom))
        cw, ch = occupied.size
        ax, ay = anchor
        local_ax, local_ay = ax - left, ay - top
        pad = int(max(cw, ch, abs(local_ax), abs(local_ay),
                      abs(cw-local_ax), abs(ch-local_ay)) * 3 + 4)
        surface = Image.new('L', (cw + 2*pad, ch + 2*pad))
        surface.paste(occupied, (pad, pad))
        alpha = surface.rotate(float(angle), Image.Resampling.NEAREST,
                               center=(pad + local_ax, pad + local_ay), expand=False)
        x, y = int(x) + left - pad, int(y) + top - pad
    bounds = alpha.getbbox()
    if bounds is None:
        return False
    left, top, right, bottom = bounds
    width, height = canvas_size
    return (x + left >= 0 and y + top >= 0
            and x + right <= width and y + bottom <= height)
