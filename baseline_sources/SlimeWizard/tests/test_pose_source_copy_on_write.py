"""Saved-frame source edits must be isolated and recoverable."""
import pytest
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


def setup():
    model = PetSuiteModel((8, 8))
    model.import_part('cat', Image.new('RGBA', (2, 2), 'red'))
    model.insert_frame('idle', 0)
    model.insert_frame('idle', 1)
    return model


def test_erase_one_pose_keeps_other_pose_and_live_buffers():
    model = setup()
    original = model.animations['idle'][1][0]['source_png']
    live = model.originals[0].tobytes()
    assert model.erase_pose_source_pixels('idle', 0, 0, {0}) is True
    assert model._decode_source(model.animations['idle'][0][0]['source_png']).getpixel((0, 0))[3] == 0
    assert model.animations['idle'][1][0]['source_png'] == original
    assert model.originals[0].tobytes() == live
    assert model.parts[0]['image'].tobytes() == live


def test_pose_source_erase_can_be_recovered():
    model = setup()
    before = model.animations['idle'][0][0]['source_png']
    model.erase_pose_source_pixels('idle', 0, 0, {0})
    assert model.restore_previous_pose('idle', 0) is True
    assert model.animations['idle'][0][0]['source_png'] == before


def test_invalid_target_does_not_mutate_frame():
    model = setup()
    before = model.animations['idle'][0][0]['source_png']
    with pytest.raises(IndexError):
        model.erase_pose_source_pixels('idle', 0, 99, {0})
    assert model.animations['idle'][0][0]['source_png'] == before


def test_empty_erase_does_not_add_recovery_version():
    model = setup()
    assert model.erase_pose_source_pixels('idle', 0, 0, set()) is False
    assert not model.pose_recovery
