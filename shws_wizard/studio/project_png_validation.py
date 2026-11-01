"""Read-only PNG integrity preflight before loading a creature project."""
from pathlib import Path
from PIL import Image, UnidentifiedImageError


class InvalidProjectArtworkError(ValueError):
    """An artwork file exists but cannot safely be decoded as a complete PNG."""


def validate_project_pngs(project_path, data):
    """Decode every required PNG without mutating any project or artwork files.

    Missing files are handled separately by require_project_assets. Modern names
    take precedence over legacy names, exactly as in the actual project loader.
    """
    project = Path(project_path)
    folder_name = data.get('asset_dir')
    folder = project.parent / folder_name if folder_name else project.with_suffix('')
    for index in range(len(data['parts'])):
        modern = folder / f'original_{index:03d}.png'
        legacy = folder / f'part_{index:03d}.png'
        source = modern if modern.exists() else legacy
        try:
            with Image.open(source) as image:
                if image.format != 'PNG':
                    raise ValueError('file is not a PNG')
                image.verify()
            # verify() checks structure; load() also detects truncated pixel data.
            with Image.open(source) as image:
                image.load()
        except (OSError, ValueError, SyntaxError, UnidentifiedImageError) as exc:
            raise InvalidProjectArtworkError(
                f'Cannot open creature: artwork {source.name} in {folder} is damaged '
                'or is not a readable PNG. The project was not changed. '
                'Restore this file from a complete backup before reopening.'
            ) from exc
