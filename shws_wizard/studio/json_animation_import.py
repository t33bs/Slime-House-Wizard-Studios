"""Import exported animation JSON + its PNG(s) as an editable, flattened pose timeline.

This does not claim to restore rigging layers: each frame is one independent,
full-canvas, paintable PNG source. All project files remain untouched.
"""
import json
import math
from pathlib import Path

from PIL import Image

from .pet_suite_model import PetSuiteModel


def is_animation_manifest(data):
    return (isinstance(data, dict) and 'parts' not in data
            and isinstance(data.get('frames'), list)
            and 'frame_size' in data)


def _dimensions(raw, description):
    if (not isinstance(raw, list) or len(raw) != 2 or
        any(isinstance(n, bool) or not isinstance(n, int) or n < 1 or n > 4096 for n in raw)):
        raise ValueError(f'{description} must contain two positive pixel sizes (up to 4096).')
    return tuple(raw)


def _png(source, expected_size):
    if not source.is_file():
        raise FileNotFoundError(f'Missing animation PNG: {source}. Keep it beside its JSON manifest.')
    try:
        with Image.open(source) as image:
            if image.format != 'PNG' or image.size != expected_size:
                raise ValueError(f'Animation PNG dimensions/format mismatch: {source.name}.')
            image.load()
            return image.convert('RGBA').copy()
    except (OSError, SyntaxError) as exc:
        raise ValueError(f'Cannot read animation PNG {source.name}.') from exc


def import_animation_manifest(path, data=None):
    """Return an unsaved editable project reconstructed from real exported PNGs."""
    path = Path(path)
    if data is None:
        data = json.loads(path.read_text(encoding='utf-8'))
    if not is_animation_manifest(data):
        raise ValueError('Not an animation export manifest.')
    width, height = _dimensions(data['frame_size'], 'Frame size')
    entries = data['frames']
    if not 0 < len(entries) <= 2000:
        raise ValueError('Animation manifest must list between 1 and 2000 frames.')
    sheet = None
    if 'sheet_size' in data:
        size = _dimensions(data['sheet_size'], 'Sprite sheet size')
        sheet = _png(path.with_suffix('.png'), size)
    model = PetSuiteModel((width, height))
    # First validate/decode all frames before publishing the model into the UI.
    prepared = []
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ValueError(f'Frame {i+1} must be an object.')
        name = entry.get('animation', 'Imported Animation')
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f'Frame {i+1} needs an animation name.')
        duration = entry.get('duration_ms', 125)
        if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not math.isfinite(duration) or not 1 <= duration <= 60000:
            raise ValueError(f'Frame {i+1} has an invalid duration.')
        if sheet is not None:
            rect = entry.get('rect')
            if not isinstance(rect, dict):
                raise ValueError(f'Frame {i+1} needs sprite-sheet coordinates.')
            x, y, w, h = (rect.get(k) for k in ('x', 'y', 'w', 'h'))
            if (any(isinstance(v, bool) or not isinstance(v, int) for v in (x, y, w, h))
                    or x < 0 or y < 0 or (w, h) != (width, height)
                    or x + w > sheet.width or y + h > sheet.height):
                raise ValueError(f'Frame {i+1} has invalid sprite-sheet bounds.')
            frame = sheet.crop((x, y, x + w, y + h))
        else:
            filename = entry.get('file')
            if (not isinstance(filename, str) or not filename or filename in ('.', '..')
                    or filename != Path(filename).name or '\\' in filename or '/' in filename):
                raise ValueError(f'Frame {i+1} has an unsafe PNG filename.')
            frame = _png(path.parent / filename, (width, height))
        prepared.append((name, round(duration), frame))
    model.import_part('Imported frame artwork', prepared[0][2])
    state = model.snapshot()[0]
    for animation, duration, frame in prepared:
        pose = [dict(state, source_png=model._encode_source(frame))]
        index = model.insert_frame(animation, len(model.animations.get(animation, [])), pose)
        model.frame_durations[animation][index] = duration
    first = prepared[0][0]
    model.current = first
    model.apply_pose(model.animations[first][0])
    return model
