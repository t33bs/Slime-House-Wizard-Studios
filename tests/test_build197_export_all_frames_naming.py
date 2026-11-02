"""Regression: Export All Frames never inherits old Friendly/project/reference filenames."""
import json
from pathlib import Path

from PIL import Image
import pytest

from shws_wizard.studio.frame_export_naming import (
    normalize_frame_export_prefix, numbered_frame_name,
    prefix_from_frame_manifest_choice,
)
from shws_wizard.studio.pet_suite_model import PetSuiteModel
from shws_wizard.studio.json_animation_import import import_animation_manifest


def _model():
    model = PetSuiteModel((64, 48))
    art = Image.new('RGBA', (64, 48))
    art.putpixel((3, 3), (31, 49, 82, 255))
    model.import_part('OLD REFERENCE ART title', art)
    for i in range(3):
        model.parts[0]['x'] = i * 2
        model.save_frame('Old Project - Walk')
        model.set_frame_duration('Old Project - Walk', i, 80 + i * 10)
    for i in range(2):
        model.parts[0]['y'] = i + 1
        model.save_frame('Side Step / Effect')
        model.set_frame_duration('Side Step / Effect', i, 110 + i * 20)
    return model


@pytest.mark.parametrize('choice,expected', [
    ('SwordcatWalk_frames.json', 'SwordcatWalk'),
    ('SwordcatWalk.json', 'SwordcatWalk'),
    ('SwordcatWalk', 'SwordcatWalk'),
    ('my.walk_frames.json', 'my_walk'),
    ('Your Animation_frames.json', 'Your_Animation'),
    ('Creature_FRAMES.JSON', 'Creature'),
])
def test_name_comes_from_user_dialog_choice_only(choice, expected):
    assert prefix_from_frame_manifest_choice(choice) == expected


def test_no_old_generic_friendly_default_or_project_names(tmp_path):
    model = _model()
    path = tmp_path / 'SwordcatWalk_frames.json'
    prefix = prefix_from_frame_manifest_choice(str(path))
    images, metadata = model.export_individual_frames(path.parent, prefix)
    assert [x.name for x in images] == [f'SwordcatWalk_frame_{i:04d}.png' for i in range(1, 6)]
    assert metadata.name == 'SwordcatWalk_frames.json'
    manifest = json.loads(metadata.read_text())
    assert [x['file'] for x in manifest['frames']] == [p.name for p in images]
    assert [x['animation'] for x in manifest['frames']] == ['Old Project - Walk'] * 3 + ['Side Step / Effect'] * 2
    assert [x['duration_ms'] for x in manifest['frames']] == [80, 90, 100, 110, 130]
    for name in [p.name for p in images]:
        assert 'OLD' not in name and 'Old' not in name and 'Friendly' not in name
        assert 'Walk' not in name.removeprefix('SwordcatWalk')
    reimported = import_animation_manifest(metadata)
    for animation, poses in model.animations.items():
        assert len(reimported.animations[animation]) == len(poses)
        assert reimported.frame_durations[animation] == model.frame_durations[animation]
        assert [reimported.render(p).tobytes() for p in reimported.animations[animation]] == [model.render(p).tobytes() for p in poses]


def test_no_source_mutation_or_default_metadata_overwrite(tmp_path):
    model = _model()
    before = model.content_fingerprint()
    images, metadata = model.export_individual_frames(tmp_path, 'NewName')
    assert model.content_fingerprint() == before
    assert metadata.name == 'NewName_frames.json'
    assert all(p.is_file() for p in images)


def test_prefix_validation_windows_portability():
    assert numbered_frame_name('creature', 1) == 'creature_frame_0001.png'
    assert normalize_frame_export_prefix('Swordcat: Night*') == 'Swordcat_Night'
    with pytest.raises(ValueError, match='Choose a name'):
        prefix_from_frame_manifest_choice('___frames.json')
    with pytest.raises(ValueError, match='Windows-reserved'):
        normalize_frame_export_prefix('CON')
    with pytest.raises(ValueError, match='starts at 1'):
        numbered_frame_name('hero', 0)


def test_gui_source_does_not_use_legacy_export_all_frames_default():
    source = (Path(__file__).parents[1] / 'shws_wizard/friendly_animator.py').read_text()
    method = source.split('    def export_all_frames(self):', 1)[1].split('    def choose_shs_location', 1)[0]
    assert 'friendly_frames' not in method
    assert 'creature_frames.json' in method
    assert 'prefix_from_frame_manifest_choice' in method
