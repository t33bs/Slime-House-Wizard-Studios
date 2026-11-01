"""SHS Chameleon: exact 2x2 RGBA source pattern, repeatable native-pixel stamping."""
from PIL import Image


def sample_2x2(image: Image.Image, x: int, y: int) -> Image.Image:
    if x < 0 or y < 0 or x+2 > image.width or y+2 > image.height:
        raise ValueError('Choose a position with a full 2 × 2 pixel block inside the canvas.')
    return image.convert('RGBA').crop((x,y,x+2,y+2))


def stamp_2x2(layer: Image.Image, pattern: Image.Image, x: int, y: int) -> None:
    """Copy exact RGBA values, including alpha, no interpolation or blending."""
    if pattern.mode != 'RGBA' or pattern.size != (2,2) or layer.mode != 'RGBA':
        raise ValueError('Chameleon requires an RGBA layer and RGBA 2 × 2 sample.')
    if x < 0 or y < 0 or x+2 > layer.width or y+2 > layer.height:
        raise ValueError('The complete 2 × 2 stamp must fit inside the selected layer.')
    layer.paste(pattern,(x,y))
