"""Crash recovery snapshots for Friendly Animator (independent of the GUI)."""
from pathlib import Path
import tempfile


def recovery_path():
    return Path(tempfile.gettempdir()) / 'slime_house_friendly_animator' / 'recovery.rig.json'


def write_recovery(model, path=None):
    """Stage and validate a snapshot before publishing; retain previous on errors."""
    import shutil
    import uuid
    path = Path(path) if path is not None else recovery_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    token = uuid.uuid4().hex
    staging = path.with_name(f'_staging_{token}.rig.json')
    staged_asset_dir = None
    published = False
    try:
        model.save_project(staging)
        import json
        staged_asset_dir = json.loads(staging.read_text(encoding='utf-8')).get('asset_dir')
        read_recovery(staging)
        # The manifest is published last; its referenced asset directory
        # remains untouched so no path rewrite or partial asset swap occurs.
        staging.replace(path)
        published = True
        return path
    finally:
        staging.unlink(missing_ok=True)
        if not published and staged_asset_dir:
            shutil.rmtree(path.parent / staged_asset_dir, ignore_errors=True)


def read_recovery(path=None):
    from studio.pet_suite_model import PetSuiteModel
    path = Path(path) if path is not None else recovery_path()
    return PetSuiteModel.load_project(path)


def discard_recovery(path=None):
    import shutil
    path = Path(path) if path is not None else recovery_path()
    if path.exists():
        import json
        try:
            asset_dir = json.loads(path.read_text(encoding='utf-8')).get('asset_dir')
            if asset_dir and Path(asset_dir).name == asset_dir:
                shutil.rmtree(path.parent / asset_dir, ignore_errors=True)
        except (OSError, ValueError, TypeError):
            pass
    path.unlink(missing_ok=True)
    shutil.rmtree(path.with_suffix(''), ignore_errors=True)


def recovery_directory():
    return recovery_path().parent / 'projects'

def list_project_recoveries(directory=None):
    """Return all independent, complete recovery project files."""
    root=Path(directory) if directory is not None else recovery_directory()
    return sorted(root.glob('creature_*.rig.json')) if root.exists() else []

def write_project_recovery(model, project_id, directory=None):
    root=Path(directory) if directory is not None else recovery_directory()
    if not isinstance(project_id,int) or project_id<0:raise ValueError('Invalid project id')
    return write_recovery(model,root / f'creature_{project_id}.rig.json')

def discard_project_recovery(project_id, directory=None):
    root=Path(directory) if directory is not None else recovery_directory()
    discard_recovery(root / f'creature_{project_id}.rig.json')
