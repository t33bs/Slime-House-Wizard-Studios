"""Conservative inspection and opt-in cleanup of orphaned project asset versions.

Never run cleanup automatically. The currently committed manifest is the sole
source of truth; unknown folders and other projects are not touched.
"""
import json
from pathlib import Path
import re
import shutil


def inspect_asset_versions(project_path):
    """Return active and orphaned version folders without changing any files."""
    project = Path(project_path)
    if not project.is_file():
        raise FileNotFoundError(project)
    manifest = json.loads(project.read_text(encoding='utf-8'))
    active = manifest.get('asset_dir')
    if not isinstance(active, str) or not re.fullmatch(
            re.escape(project.stem) + r'_assets_[0-9a-f]{32}', active):
        # Legacy or unexpected layout: never guess what can be deleted.
        return {'active': None, 'orphans': [], 'safe_to_clean': False}
    active_path = project.parent / active
    if not active_path.is_dir():
        raise FileNotFoundError(active_path)
    prefix = re.compile(re.escape(project.stem) + r'_assets_[0-9a-f]{32}\Z')
    orphans = sorted(p for p in project.parent.iterdir()
                     if p.is_dir() and not p.is_symlink() and prefix.fullmatch(p.name)
                     and p.name != active)
    return {'active': active_path, 'orphans': orphans, 'safe_to_clean': True}


def cleanup_asset_versions(project_path, *, confirmed=False, backup_roots=(),
                           backup_inventory_complete=False):
    """Delete unreferenced versions only after a complete backup inventory.

    ``confirmed`` is the user's deletion approval; ``backup_inventory_complete``
    is a separate caller assertion that ALL locations containing project backups
    have been supplied in ``backup_roots``. If that cannot be established, do
    not delete anything. The UI does not currently expose this operation.
    """
    result = inspect_asset_versions(project_path)
    if not (confirmed and backup_inventory_complete and result['safe_to_clean']):
        return []
    project = Path(project_path).resolve()
    roots = [project.parent]
    for root in backup_roots:
        path = Path(root).resolve()
        if not path.is_dir():
            return []
        if path not in roots:
            roots.append(path)
    references = set()
    for root in roots:
        # Recursive scan covers backup subdirectories and recovery snapshots.
        # An unreadable or malformed JSON file is treated as a blocker.
        try:
            manifests = list(root.rglob('*.json'))
        except OSError:
            return []
        for manifest_path in manifests:
            try:
                if manifest_path.is_symlink():
                    return []
                entry = json.loads(manifest_path.read_text(encoding='utf-8'))
                if isinstance(entry, dict) and isinstance(entry.get('asset_dir'), str):
                    references.add(entry['asset_dir'])
            except (OSError, ValueError, UnicodeError):
                return []
    # Recheck the active manifest immediately before deleting anything.
    fresh = inspect_asset_versions(project)
    # Windows may expand an 8.3 short parent path (RUNNER~1) when
    # resolving the project. Compare canonical paths, not spellings.
    if fresh['active'].resolve() != result['active'].resolve():
        return []
    removed = []
    for folder in fresh['orphans']:
        if folder.name in references:
            continue
        shutil.rmtree(folder)
        removed.append(folder)
    return removed


def report_asset_recovery(project_path, *, backup_roots=()):
    """Read-only inventory of saved asset versions and known backup references.

    This is informational, not proof that an asset is safe to delete. Unknown
    backup locations are inherently outside the report's visibility.
    """
    project = Path(project_path)
    if not project.is_file():
        raise FileNotFoundError(project)
    manifest = json.loads(project.read_text(encoding='utf-8'))
    active_name = manifest.get('asset_dir')
    prefix = re.compile(re.escape(project.stem) + r'_assets_[0-9a-f]{32}\Z')
    roots = [project.parent]
    warnings = []
    for candidate in backup_roots:
        root = Path(candidate)
        if not root.is_dir():
            warnings.append(f'Backup location unavailable: {root}')
        elif root not in roots:
            roots.append(root)
    references = {}
    for root in roots:
        try:
            paths = list(root.rglob('*.json'))
        except OSError as exc:
            warnings.append(f'Cannot scan {root}: {exc}')
            continue
        for path in paths:
            try:
                if path.is_symlink():
                    warnings.append(f'Symlinked manifest not inspected: {path}')
                    continue
                data = json.loads(path.read_text(encoding='utf-8'))
                if isinstance(data, dict) and isinstance(data.get('asset_dir'), str):
                    references.setdefault(data['asset_dir'], []).append(str(path))
            except (OSError, ValueError, UnicodeError) as exc:
                warnings.append(f'Cannot read manifest {path}: {exc}')
    names = set(references)
    if isinstance(active_name, str):
        names.add(active_name)
    for path in project.parent.iterdir():
        if path.is_dir() and not path.is_symlink() and prefix.fullmatch(path.name):
            names.add(path.name)
    versions = []
    for name in sorted(names):
        if not prefix.fullmatch(name):
            continue
        folder = project.parent / name
        versions.append({
            'name': name,
            'status': 'missing' if not folder.is_dir() else ('active' if name == active_name else 'available'),
            'referenced_by': sorted(references.get(name, [])),
            'png_count': sum(1 for _ in folder.glob('*.png')) if folder.is_dir() else 0,
        })
    if not isinstance(active_name, str) or not prefix.fullmatch(active_name):
        warnings.append('Legacy or unexpected active asset layout; version report may be incomplete')
    return {'project': str(project), 'versions': versions,
            'warnings': warnings,
            'note': 'Read-only report. Unlisted backup locations may reference any version; never infer deletion safety.'}
