"""Phase 15: history branching and mutable pixel buffers must remain isolated."""
from PIL import Image
from studio.edit_history import EditHistory, capture
from studio.pet_suite_model import PetSuiteModel


def _model():
    model = PetSuiteModel()
    image = Image.new('RGBA', (8, 8))
    image.putpixel((1, 1), (255, 0, 0, 255))
    model.import_part('sprite', image)
    return model


def test_undo_then_new_edit_discards_old_redo_branch():
    model = _model()
    history = EditHistory()
    history.record(model)
    model.parts[0]['x'] = 4
    history.record(model)
    model.parts[0]['x'] = 8
    assert history.undo(model)
    assert model.parts[0]['x'] == 4
    history.record(model)
    model.parts[0]['x'] = 12
    assert not history.redo(model)
    assert model.parts[0]['x'] == 12
    assert history.undo(model)
    assert model.parts[0]['x'] == 4
    assert history.redo(model)
    assert model.parts[0]['x'] == 12


def test_saved_pose_pixels_and_history_are_deep_copied():
    model = _model()
    animation = 'Walk'
    model.insert_frame(animation, 0)
    history = EditHistory()
    initial = capture(model)
    history.record(model)
    model.originals[0].putpixel((1, 1), (0, 0, 0, 0))
    model.resize_part(0, 8, 8)
    model.insert_frame(animation, 1)
    assert model._decode_source(model.animations[animation][0][0]['source_png']).getpixel((1, 1)) == (255, 0, 0, 255)
    assert model._decode_source(model.animations[animation][1][0]['source_png']).getpixel((1, 1)) == (0, 0, 0, 0)
    assert history.undo(model)
    assert capture(model) == initial
    assert model.parts[0]['image'].getpixel((1, 1)) == (255, 0, 0, 255)
