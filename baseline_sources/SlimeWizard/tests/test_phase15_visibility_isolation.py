"""Phase 15: per-pose visibility edits must never leak to neighboring poses."""
from copy import deepcopy

from PIL import Image

from studio.edit_history import EditHistory, capture
from studio.pet_suite_model import PetSuiteModel


def _three_pose_model():
    model = PetSuiteModel()
    model.import_part('body', Image.new('RGBA', (8, 8), (255, 0, 0, 255)))
    model.import_part('accessory', Image.new('RGBA', (2, 2), (0, 255, 0, 255)))
    for x in (1, 2, 3):
        model.parts[1]['x'] = x
        model.insert_frame('Walk', len(model.animations.get('Walk', [])))
    return model


def test_hide_restore_middle_pose_preserves_neighbors_and_source_assets():
    model = _three_pose_model()
    neighbors = (deepcopy(model.animations['Walk'][0]), deepcopy(model.animations['Walk'][2]))
    originals = [image.tobytes() for image in model.originals]
    model.edit_pose_at('Walk', 1, {1: {'visible': False}})
    assert model.animations['Walk'][1][1]['visible'] is False
    assert model.animations['Walk'][0] == neighbors[0]
    assert model.animations['Walk'][2] == neighbors[1]
    assert [image.tobytes() for image in model.originals] == originals
    model.edit_pose_at('Walk', 1, {1: {'visible': True}})
    assert model.animations['Walk'][1][1]['visible'] is True
    assert model.animations['Walk'][0] == neighbors[0]
    assert model.animations['Walk'][2] == neighbors[1]


def test_visibility_edits_undo_redo_without_changing_pose_count():
    model = _three_pose_model()
    history = EditHistory()
    initial = capture(model)
    history.record(model)
    model.edit_pose_at('Walk', 1, {1: {'visible': False}})
    hidden = capture(model)
    history.record(model)
    model.edit_pose_at('Walk', 1, {1: {'visible': True}})
    restored = capture(model)
    assert len(model.animations['Walk']) == 3
    assert history.undo(model) and capture(model) == hidden
    assert history.undo(model) and capture(model) == initial
    assert history.redo(model) and capture(model) == hidden
    assert history.redo(model) and capture(model) == restored
    assert len(model.animations['Walk']) == 3
