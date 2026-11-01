"""Saved pose selection erase is isolated and rejects ambiguous footprints."""
import pytest
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


def make_model():
    model = PetSuiteModel((12, 12))
    model.import_part('cat', Image.new('RGBA', (2, 2), 'red'))
    model.insert_frame('idle', 0)
    model.insert_frame('idle', 1)
    return model


def test_complete_scaled_selection_edits_only_one_saved_pose():
    model = make_model()
    state = model.animations['idle'][0][0]
    state.update(x=2, y=2, width=4, height=4)
    mask = Image.new('L', model.size)
    for y in (2, 3):
        for x in (2, 3):
            mask.putpixel((x, y), 255)
    other = model.animations['idle'][1][0]['source_png']
    live = model.originals[0].tobytes()
    assert model.erase_selected_pose_pixels('idle', 0, 0, mask)
    assert model._decode_source(model.animations['idle'][0][0]['source_png']).getpixel((0, 0))[3] == 0
    assert model.animations['idle'][1][0]['source_png'] == other
    assert model.originals[0].tobytes() == live
    assert model.restore_previous_pose('idle', 0)
    assert model._decode_source(model.animations['idle'][0][0]['source_png']).getpixel((0, 0))[3] == 255


def test_partial_scaled_selection_is_rejected_without_mutation():
    model = make_model()
    model.animations['idle'][0][0].update(x=2, y=2, width=4, height=4)
    mask = Image.new('L', model.size)
    mask.putpixel((2, 2), 255)
    before = model.animations['idle'][0][0]['source_png']
    with pytest.raises(ValueError, match='part of'):
        model.erase_selected_pose_pixels('idle', 0, 0, mask)
    assert model.animations['idle'][0][0]['source_png'] == before
    assert not model.pose_recovery


def test_multiple_visible_layers_are_rejected():
    model = make_model()
    model.import_part('hat', Image.new('RGBA', (1, 1), 'blue'))
    model.insert_frame('idle', 2)
    mask = Image.new('L', model.size, 255)
    with pytest.raises(ValueError, match='one visible part'):
        model.erase_selected_pose_pixels('idle', 2, 0, mask)


def test_wrong_mask_size_rejected():
    model = make_model()
    with pytest.raises(ValueError, match='canvas size'):
        model.erase_selected_pose_pixels('idle', 0, 0, Image.new('L', (2, 2)))


def test_rotated_complete_source_footprint_preserves_other_frames():
    from studio.pixel_source_mapping import rendered_source_indices
    model = make_model()
    state = model.animations['idle'][0][0]
    state.update(x=4, y=4, width=4, height=4, angle=90)
    mapping = rendered_source_indices((2, 2), model.size, 4, 4, 4, 4, 90, (2, 2))
    mask = Image.new('L', model.size)
    for y in range(model.size[1]):
        for x in range(model.size[0]):
            if mapping.getpixel((x, y)) == 1:
                mask.putpixel((x, y), 255)
    assert mask.getbbox() is not None
    before = model.animations['idle'][1][0]['source_png']
    assert model.erase_selected_pose_pixels('idle', 0, 0, mask)
    assert model._decode_source(model.animations['idle'][0][0]['source_png']).getpixel((0, 0))[3] == 0
    assert model.animations['idle'][1][0]['source_png'] == before

def test_rgb_mask_is_rejected_before_mutation():
    model = make_model()
    before = model.animations['idle'][0][0]['source_png']
    with pytest.raises(ValueError, match='grayscale'):
        model.erase_selected_pose_pixels('idle', 0, 0, Image.new('RGB', model.size, 'white'))
    assert model.animations['idle'][0][0]['source_png'] == before
    assert not model.pose_recovery
