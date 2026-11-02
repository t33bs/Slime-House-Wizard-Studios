"""Predictable, user-named frame exports, independent of project/reference titles.

The JSON manifest stores animation associations and durations.  Filenames are
controlled ONLY by the name selected in Export All Frames, plus a frame number.
"""
from pathlib import Path
import re


def normalize_frame_export_prefix(name: str) -> str:
    """Validate a filename prefix for Windows-compatible exports.

    This never takes a project name, source asset name, animation label, or
    remembered reference filename as an implicit prefix.
    """
    raw = str(name).strip()
    raw = re.sub(r'[^\w-]+', '_', raw, flags=re.UNICODE).strip('_')
    if not raw or raw in ('.', '..'):
        raise ValueError('Choose a name for the exported animation frames.')
    # Windows reserved device names are invalid, even with an extension.
    if raw.upper() in {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}:
        raise ValueError('Choose a different frame export name (Windows-reserved filename).')
    return raw


def prefix_from_frame_manifest_choice(filename: str) -> str:
    """A Save dialog choice like `SwordcatWalk_frames.json` -> `SwordcatWalk`."""
    chosen = Path(filename).name
    if chosen.lower().endswith('.json'):
        chosen = chosen[:-5]
    if chosen.lower().endswith('_frames'):
        chosen = chosen[:-7]
    return normalize_frame_export_prefix(chosen)


def numbered_frame_name(prefix: str, index: int) -> str:
    if index < 1:
        raise ValueError('Frame numbering starts at 1.')
    return f'{normalize_frame_export_prefix(prefix)}_frame_{index:04d}.png'
