import json
import pytest
from studio.project_recovery import (diagnose_project_assets, require_project_assets,
                                     MissingProjectAssetsError)


def test_missing_assets_report_and_safe_error(tmp_path):
    project = tmp_path / 'creature.json'
    folder = tmp_path / ('creature_assets_' + __import__('uuid').uuid4().hex)
    folder.mkdir()
    project.write_text(json.dumps({'asset_dir': folder.name, 'parts': [{'name': 'cat'}]}))
    before = project.read_bytes()
    report = diagnose_project_assets(project)
    assert len(report['missing']) == 1
    with pytest.raises(MissingProjectAssetsError, match='Your project was not changed'):
        require_project_assets(project)
    assert project.read_bytes() == before


def test_legacy_asset_name_accepted(tmp_path):
    project = tmp_path / 'cat.json'
    folder = tmp_path / 'cat'
    folder.mkdir()
    (folder / 'part_000.png').write_bytes(b'placeholder')
    project.write_text(json.dumps({'parts': [{'name': 'cat'}]}))
    assert require_project_assets(project)['missing'] == []


def test_asset_directory_traversal_rejected(tmp_path):
    project = tmp_path / 'cat.json'
    project.write_text(json.dumps({'asset_dir': '../outside', 'parts': []}))
    with pytest.raises(ValueError, match='Invalid project asset directory'):
        diagnose_project_assets(project)
