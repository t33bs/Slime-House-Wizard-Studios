"""Plain .json compatibility: independently editable legacy rig or frame export."""
from copy import deepcopy
import json
from pathlib import Path
import shutil

from PIL import Image
import pytest

from shws_wizard.studio.json_animation_import import import_animation_manifest
from shws_wizard.studio.pet_suite_model import PetSuiteModel
from shws_wizard.studio.project_recovery import MissingProjectAssetsError


def _rig(tmp_path):
    model = PetSuiteModel((96, 160))
    art = Image.new('RGBA', (96, 160))
    art.putpixel((11, 13), (185, 55, 94, 255))
    model.import_part('Creature', art)
    for i in range(9):
        model.parts[0]['x'] = i
        model.save_frame('Walk')
        model.set_frame_duration('Walk', i, 90 + i * 5)
    path = tmp_path / 'mycreature.json'
    model.save_project(path)
    return model, path


def test_plain_json_legacy_with_missing_assets_recovers_embedded_png_no_mutations(tmp_path):
    original, path = _rig(tmp_path)
    expected = [original.render(p).tobytes() for p in original.animations['Walk']]
    source = path.read_bytes()
    asset = tmp_path / json.loads(source)['asset_dir']
    shutil.rmtree(asset)
    recovered = PetSuiteModel.load_project(path)
    assert recovered.size == (96, 160)
    assert [recovered.render(p).tobytes() for p in recovered.animations['Walk']] == expected
    assert recovered.frame_durations['Walk'] == original.frame_durations['Walk']
    assert recovered.pose_ids == original.pose_ids
    assert path.read_bytes() == source and not asset.exists()
    saved = tmp_path / 'recovered.rig.json'
    recovered.save_project(saved)
    again = PetSuiteModel.load_project(saved)
    assert [again.render(p).tobytes() for p in again.animations['Walk']] == expected


def test_missing_png_without_inline_png_does_not_silently_open(tmp_path):
    _, path = _rig(tmp_path)
    data = json.loads(path.read_text())
    shutil.rmtree(tmp_path / data['asset_dir'])
    data['parts'][0].pop('source_png')
    path.write_text(json.dumps(data))
    with pytest.raises(MissingProjectAssetsError, match='artwork PNG'):
        PetSuiteModel.load_project(path)


def test_corrupt_embedded_source_rejected_no_change(tmp_path):
    _, path = _rig(tmp_path)
    data = json.loads(path.read_text())
    shutil.rmtree(tmp_path / data['asset_dir'])
    data['parts'][0]['source_png'] = '%%%invalid%%%'
    source = json.dumps(data)
    path.write_text(source)
    with pytest.raises(ValueError, match='embedded PNG'):
        PetSuiteModel.load_project(path)
    assert path.read_text() == source


def test_preexisting_corrupt_png_not_replaced_by_embedded_source(tmp_path):
    _, path = _rig(tmp_path)
    folder = tmp_path / json.loads(path.read_text())['asset_dir']
    (folder / 'original_000.png').write_bytes(b'not an image')
    with pytest.raises(Exception):
        PetSuiteModel.load_project(path)


def _sheet(tmp_path):
    model = PetSuiteModel((64, 48))
    for i in range(9):
        art = Image.new('RGBA', (64, 48))
        art.putpixel((10+i, 13), (30 + i, 80, 140, 255))
        model.import_part(f'Layer {i}', art)
        for part in model.parts:
            part['visible'] = False
        model.parts[-1]['visible'] = True
        model.save_frame('Walk')
        model.set_frame_duration('Walk', i, 100 + 10 * i)
    expected = [model.render(p).tobytes() for p in model.animations['Walk']]
    model.export(tmp_path, 'walk')
    return tmp_path / 'walk_sheet.json', expected


def test_sheet_manifest_import_nine_independent_frames_then_save_as(tmp_path):
    path, expected = _sheet(tmp_path)
    untouched_manifest, untouched_png = path.read_bytes(), path.with_suffix('.png').read_bytes()
    model = import_animation_manifest(path)
    assert model.size == (64, 48)
    assert len(model.animations['Walk']) == 9
    assert len(set(model.pose_ids['Walk'])) == 9
    assert model.frame_durations['Walk'] == [100 + 10 * i for i in range(9)]
    assert [model.render(p).tobytes() for p in model.animations['Walk']] == expected
    before = [model.render(p).tobytes() for p in model.animations['Walk']]
    model.edit_pose_at('Walk', 4, {0: {'x': 2}})
    assert [model.render(p).tobytes() for p in model.animations['Walk'] if p is not model.animations['Walk'][4]] == [v for i, v in enumerate(before) if i != 4]
    result = tmp_path / 'new.rig.json'
    model.save_project(result)
    loaded = PetSuiteModel.load_project(result)
    assert [loaded.render(p).tobytes() for p in loaded.animations['Walk']] == [model.render(p).tobytes() for p in model.animations['Walk']]
    assert path.read_bytes() == untouched_manifest and path.with_suffix('.png').read_bytes() == untouched_png


def test_sheet_json_with_missing_png_is_actionable(tmp_path):
    path, _ = _sheet(tmp_path)
    path.with_suffix('.png').unlink()
    with pytest.raises(FileNotFoundError, match='Keep it beside'):
        import_animation_manifest(path)


def test_sheet_json_rejects_out_of_bounds_rect_and_unsafe_frame_file(tmp_path):
    path, _ = _sheet(tmp_path)
    data = json.loads(path.read_text())
    data['frames'][0]['rect']['x'] = 9999
    with pytest.raises(ValueError, match='bounds'):
        import_animation_manifest(path, data)
    data = {'frame_size': [64, 48], 'frames': [{'animation': 'Walk', 'duration_ms':125, 'file':'../bad.png'}]}
    with pytest.raises(ValueError, match='unsafe'):
        import_animation_manifest(tmp_path / 'frames.json', data)


def test_individual_frame_export_manifest_roundtrip(tmp_path):
    source = PetSuiteModel((32, 24))
    source.import_part('Hero', Image.new('RGBA', (32, 24), (90, 20, 30, 255)))
    for i in range(3):
        source.parts[0]['x'] = i
        source.save_frame('Idle')
    expected = [source.render(p).tobytes() for p in source.animations['Idle']]
    _, metadata = source.export_individual_frames(tmp_path, basename='hero')
    imported = import_animation_manifest(metadata)
    assert len(imported.animations['Idle']) == 3
    assert [imported.render(p).tobytes() for p in imported.animations['Idle']] == expected


def test_ui_dialog_shows_all_json_files_by_default():
    source = (Path(__file__).parents[1] / 'shws_wizard/friendly_animator.py').read_text()
    assert 'Creature or animation JSON (*.rig.json *.json)' in source
    assert 'import_animation_manifest(path,manifest)' in source
    assert "self.add_project(model,Path(path).stem+' (imported animation)')" in source
