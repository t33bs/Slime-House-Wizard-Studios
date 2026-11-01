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
    size = data.get('size')
    if not isinstance(size, (list, tuple)) or len(size) != 2:
        _error('canvas size', 'must contain width and height')
    for i, value in enumerate(size):
        _positive_dimension(value, f'canvas size[{i}]')
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
    return data


def validate_project_file(path):
    path = Path(path)
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise InvalidProjectDataError('Cannot open creature: project JSON is damaged. The project was not changed.') from exc
    return validate_project_data(data)
