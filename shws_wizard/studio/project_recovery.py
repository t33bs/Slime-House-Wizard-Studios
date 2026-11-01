"""Read-only diagnostics for projects with missing PNG assets."""
import json
from pathlib import Path


class MissingProjectAssetsError(FileNotFoundError):
    """Actionable error; loading must not modify the project on disk."""


def diagnose_project_assets(project_path):
    """Check every expected original PNG before loading any into the editor."""
    project = Path(project_path)
    data = json.loads(project.read_text(encoding='utf-8'))
    folder_name = data.get('asset_dir')
    if folder_name is not None and (
        not isinstance(folder_name, str) or Path(folder_name).name != folder_name
        or folder_name in ('.', '..')
    ):
        raise ValueError('Invalid project asset directory')
    folder = project.parent / folder_name if folder_name else project.with_suffix('')
    missing = []
    for i, _ in enumerate(data['parts']):
        modern = folder / f'original_{i:03d}.png'
        legacy = folder / f'part_{i:03d}.png'
        if not modern.is_file() and not legacy.is_file():
            missing.append(modern)
    return {'project': project, 'asset_folder': folder, 'missing': missing,
            'expected_count': len(data['parts'])}


def require_project_assets(project_path):
    report = diagnose_project_assets(project_path)
    if report['missing']:
        preview = '\n'.join(f'  - {p.name}' for p in report['missing'][:8])
        remaining = len(report['missing']) - 8
        if remaining:
            preview += f'\n  ... and {remaining} more'
        raise MissingProjectAssetsError(
            f'This creature cannot be opened because {len(report["missing"])} artwork '
            f'PNG file(s) are missing from:\n{report["asset_folder"]}\n\n'
            f'Missing files:\n{preview}\n\n'
            'Your project was not changed. Restore the missing PNGs from a '
            'backup of this project, or open a complete backup copy. '
            'Do not overwrite the original project with an empty creature.'
        )
    return report
