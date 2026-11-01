"""Pixel-precise, non-destructive Slimer Tool selection and transform primitives.

The UI can hold a SlimerSelection as a temporary preview and only commit the
result after the user presses Place Frame / Place as Layer.
"""
from dataclasses import dataclass
from PIL import Image, ImageChops


def composite_selection_layers(layers, canvas_size):
    """Combine selected RGBA layers without converting partial alpha to opaque.

    Each preview already contains the original pixel opacity. A binary paste
    mask would replace a 50%-opaque pixel with its RGB at 100% opacity.
    """
    combined = Image.new('RGBA', canvas_size)
    for layer in layers:
        if layer.size != canvas_size:
            raise ValueError('Slimer preview dimensions must match the canvas')
        combined.alpha_composite(layer.convert('RGBA'))
    return combined


@dataclass
class SlimerSelection:
    source: Image.Image
    mask: Image.Image

    def __post_init__(self):
        self.source = self.source.convert('RGBA').copy()
        self.mask = self.mask.convert('L').copy()
        if self.source.size != self.mask.size:
            raise ValueError('Selection mask must match the source image size.')

    @classmethod
    def empty(cls, source):
        return cls(source, Image.new('L', source.size, 0))

    def paint(self, x, y, radius=0, erase=False):
        """Paint a square, crisp-pixel selection brush (no anti-aliasing)."""
        radius = max(0, int(radius))
        for py in range(max(0, int(y)-radius), min(self.mask.height, int(y)+radius+1)):
            for px in range(max(0, int(x)-radius), min(self.mask.width, int(x)+radius+1)):
                self.mask.putpixel((px, py), 0 if erase else 255)

    def selected_pixels(self):
        transparent = Image.new('RGBA', self.source.size)
        return Image.composite(self.source, transparent, self.mask)

    def transform(self, dx=0, dy=0, width=None, height=None, angle=0):
        """Return an RGBA full-canvas preview; nearest-neighbor transformations."""
        cut = self.selected_pixels()
        bounds = self.mask.getbbox()
        preview = Image.new('RGBA', self.source.size)
        if bounds is None:
            return preview
        piece = cut.crop(bounds)
        w = max(1, int(width if width is not None else piece.width))
        h = max(1, int(height if height is not None else piece.height))
        if (w, h) != piece.size:
            piece = piece.resize((w, h), Image.Resampling.NEAREST)
        if angle % 360:
            piece = piece.rotate(float(angle), Image.Resampling.NEAREST, expand=True)
        preview.paste(piece, (bounds[0]+int(dx), bounds[1]+int(dy)))
        return preview

    def compose(self, preview, move_original=False):
        """Commit selected pixels on top; optionally clear their old location."""
        if preview.size != self.source.size:
            raise ValueError('Preview size must match source size.')
        result = self.source.copy()
        if move_original:
            result.putalpha(ImageChops.subtract(result.getchannel('A'), self.mask))
        result.alpha_composite(preview.convert('RGBA'))
        return result
