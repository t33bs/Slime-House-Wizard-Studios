"""Build 1.9.5: custom-size creature reopen and clear JSON format errors."""
from copy import deepcopy
import json
from pathlib import Path

import pytest
from PIL import Image

from shws_wizard.studio.pet_suite_model import PetSuiteModel
from shws_wizard.studio.project_validation import (
    InvalidProjectDataError, validate_project_data,
)


@pytest.mark.parametrize('size', [(64, 64), (128, 128), (256, 256),
                                  (512, 512), (96, 160), (512, 128),
                                  (1024, 1024)])
def test_creature_reopens_at_its_saved_dimensions_with_independent_poses(tmp_path, size):
    model = PetSuiteModel(size)
    art = Image.new('RGBA', (9, 7), (0, 0, 0, 0))
    art.putpixel((2, 3), (191, 77, 124, 231))
    model.import_part('Swordcat test', art)
    animation = 'Walk'
    for n in range(7):
        model.parts[0]['x'] = n * 3
        model.parts[0]['y'] = n
        model.insert_frame(animation, n)
        model.set_frame_duration(animation, n, 125 + n * 10)
    model.current = animation
    original_poses = deepcopy(model.animations[animation])
    original_ids = model._sync_pose_ids(animation)[:]
    original_durations = model.frame_durations[animation][:]
    expected_rgba = [model.render(p).tobytes() for p in original_poses]
    filename = tmp_path / 'custom-canvas.rig.json'
    model.save_project(filename)
    manifest_bytes = filename.read_bytes()
    assert json.loads(manifest_bytes)['size'] == list(size)
    # Reopen independently of whatever canvas dimensions the live editor had.
    reopened = PetSuiteModel.load_project(filename)
    assert reopened.size == size
    assert reopened.animations[animation] == original_poses
    assert reopened._sync_pose_ids(animation) == original_ids
    assert reopened.frame_durations[animation] == original_durations
    assert [reopened.render(p).tobytes() for p in reopened.animations[animation]] == expected_rgba
    assert filename.read_bytes() == manifest_bytes
    # A subsequent save must preserve the size exactly as loaded.
    again = tmp_path / 'second-save.rig.json'
    reopened.save_project(again)
    assert PetSuiteModel.load_project(again).size == size


def test_sheet_export_json_is_not_misdiagnosed_as_canvas_resizing(tmp_path):
    model = PetSuiteModel((96, 160))
    model.import_part('Test', Image.new('RGBA', (2, 2), (2, 4, 6, 255)))
    model.save_frame('Walk')
    model.export(tmp_path, basename='walking')
    path = tmp_path / 'walking_sheet.json'
    with pytest.raises(InvalidProjectDataError, match='sprite-sheet export metadata') as exc:
        PetSuiteModel.load_project(path)
    assert 'Save Creature' in str(exc.value)
    assert 'project was not changed' in str(exc.value)
    assert 'frame_size' in json.loads(path.read_text())


@pytest.mark.parametrize('alias', ['size_dict', 'canvas_size', 'canvas_dict', 'canvas_width_height'])
def test_legacy_explicit_dimensions_open_without_changing_original(tmp_path, alias):
    model = PetSuiteModel((96, 160))
    model.import_part('Test', Image.new('RGBA', (3, 3), (19, 28, 37, 255)))
    model.save_frame('Walk')
    path = tmp_path / 'legacy.rig.json'
    model.save_project(path)
    data = json.loads(path.read_text())
    data.pop('size')
    if alias == 'size_dict':
        data['size'] = {'width': 96, 'height': 160}
    elif alias == 'canvas_size':
        data['canvas_size'] = [96, 160]
    elif alias == 'canvas_dict':
        data['canvas'] = {'width': 96, 'height': 160}
    else:
        data['canvas_width'], data['canvas_height'] = 96, 160
    original = json.dumps(data, indent=2).encode('utf-8')
    path.write_bytes(original)
    loaded = PetSuiteModel.load_project(path)
    assert loaded.size == (96, 160)
    assert loaded.animations['Walk'] == model.animations['Walk']
    assert loaded.render(loaded.animations['Walk'][0]).tobytes() == model.render(model.animations['Walk'][0]).tobytes()
    assert path.read_bytes() == original


@pytest.mark.parametrize('value', [None, {}, {'width': 80, 'height': 0},
                                    [128], [-1, 80], [True, 80], [128.2, 80]])
def test_ambiguous_or_bad_size_is_safely_rejected(value):
    data = {'version': 3, 'size': value, 'parts': [], 'animations': {}}
    with pytest.raises(InvalidProjectDataError, match='canvas size'):
        validate_project_data(data)


def test_open_dialog_prefers_real_rig_json_and_retains_legacy_files():
    src = (Path(__file__).resolve().parents[1] / 'shws_wizard' / 'friendly_animator.py').read_text()
    assert 'Creature or animation JSON (*.rig.json *.json)' in src
    assert 'Editable rig project (*.rig.json)' in src
