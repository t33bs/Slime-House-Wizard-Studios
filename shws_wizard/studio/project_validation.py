"""Non-mutating preflight checks for saved creature project manifests."""
import json
import math
from pathlib import Path


class InvalidProjectDataError(ValueError):
    """Saved project structure is damaged or unsupported."""


def _error(location, detail):
    raise InvalidProjectDataError(f'Cannot open creature: {location} {detail}. The project was not changed.')


def _positive_dimension(value, location):
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 16384:
        _error(location, 'must be a positive pixel dimension (up to 16384)')


def _pose_state(state, location):
    if not isinstance(state, dict):
        _error(location, 'must contain editable part data')
    for key in ('x', 'y'):
        value = state.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            _error(f'{location}.{key}', 'must be a finite number')
    for key in ('width', 'height'):
        _positive_dimension(state.get(key), f'{location}.{key}')
    if 'angle' in state and (not isinstance(state['angle'], (int, float)) or
                           not math.isfinite(state['angle'])):
        _error(f'{location}.angle', 'must be a finite number')


def validate_project_data(data):
    """Reject invalid structures before loading PNGs or changing live editor state."""
    if not isinstance(data, dict):
        _error('project', 'must be a JSON object')
    # A sprite-sheet export also ends in .json, but is not an editable creature.
    # Recognize it first so users do not mistake a format error for a failure
    # to resize the canvas. Never turn sheet metadata into an empty rig.
    if ('frame_size' in data and 'sheet_size' in data and 'frames' in data
            and 'parts' not in data):
        _error('selected JSON file',
               'is sprite-sheet export metadata, not an editable creature project. '
               'Use the file saved by Save Creature (usually *.rig.json). '
               'The matching *_sheet.png is an animation export, not a rig')

    size = data.get('size')
    # A few older/external editable-rig manifests use explicitly named canvas
    # dimensions. Accept them only for files that genuinely contain the
    # editable parts and animation lists, never for a sheet/preview manifest.
    if isinstance(size, dict):
        size = [size.get('width'), size.get('height')]
    elif size is None and isinstance(data.get('parts'), list) and isinstance(data.get('animations'), dict):
        alternative = data.get('canvas_size', data.get('canvas'))
        if isinstance(alternative, dict):
            size = [alternative.get('width'), alternative.get('height')]
        elif isinstance(alternative, (list, tuple)):
            size = alternative
        elif 'canvas_width' in data or 'canvas_height' in data:
            size = [data.get('canvas_width'), data.get('canvas_height')]
    if not isinstance(size, (list, tuple)) or len(size) != 2:
        _error('canvas size',
               'must contain width and height. Choose a Save Creature .rig.json '
               'project, not the JSON exported with a sprite sheet')
    for i, value in enumerate(size):
        _positive_dimension(value, f'canvas size[{i}]')
    # Normalize only in memory; opening a project must never rewrite its JSON.
    # This lets the rest of the loader restore the original non-square canvas.
    if data.get('size') != list(size):
        data = dict(data, size=list(size))
    parts = data.get('parts')
    if not isinstance(parts, list):
        _error('parts', 'must be a list')
    for i, part in enumerate(parts):
        _pose_state(part, f'parts[{i}]')
        if not isinstance(part.get('name'), str):
            _error(f'parts[{i}].name', 'must be text')
    animations = data.get('animations', {})
    if not isinstance(animations, dict):
        _error('animations', 'must be an object')
    for name, frames in animations.items():
        if not isinstance(name, str) or not isinstance(frames, list):
            _error('animation timeline', 'must have named lists of poses')
        for i, pose in enumerate(frames):
            if not isinstance(pose, list):
                _error(f'animation {name!r} pose {i+1}', 'must be a list of parts')
            if len(pose) > len(parts):
                _error(f'animation {name!r} pose {i+1}', 'references more parts than the project contains')
            for j, state in enumerate(pose):
                _pose_state(state, f'animation {name!r} pose {i+1} part {j+1}')
    durations = data.get('frame_durations', {})
    if not isinstance(durations, dict):
        _error('frame durations', 'must be an object')
    for name, values in durations.items():
        if not isinstance(values, list) or name not in animations:
            _error(f'frame durations for {name!r}', 'must belong to an animation and be a list')
        for i, value in enumerate(values):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
                _error(f'frame duration {name!r}[{i}]', 'must be a positive number')
    # An unplaced draft is NOT another saved animation pose. Verify that its
    # owner is a real stable saved pose, never an untrusted numeric row.
    draft = data.get('unplaced_next_pose')
    if draft is not None:
        if not isinstance(draft, dict) or set(draft) != {'animation', 'pose_id'}:
            _error('unplaced next pose', 'must identify its saved animation and pose')
        animation, pose_id = draft['animation'], draft['pose_id']
        pose_ids = data.get('pose_ids', {})
        if (not isinstance(animation, str) or animation not in animations
                or not isinstance(pose_id, str) or not isinstance(pose_ids, dict)
                or not isinstance(pose_ids.get(animation), list)
                or pose_id not in pose_ids[animation]):
            _error('unplaced next pose', 'references a missing saved pose identity')
    return data


def validate_project_file(path):
    path = Path(path)
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise InvalidProjectDataError('Cannot open creature: project JSON is damaged. The project was not changed.') from exc
    return validate_project_data(data)
