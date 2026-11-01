"""Phase 15 model-level timeline and undo/redo safety, independent of Qt."""
from copy import deepcopy
from PIL import Image
from studio.pet_suite_model import PetSuiteModel
from studio.edit_history import EditHistory, capture


def test_middle_insertion_preserves_neighbor_ids_durations_and_pixels():
    m = PetSuiteModel()
    m.import_part('pixel', Image.new('RGBA', (2, 2), (255, 0, 0, 255)))
    name = 'Walk'
    for x, duration in ((1, 80), (2, 160), (3, 240)):
        m.parts[0]['x'] = x
        index = m.save_frame(name)
        m.set_frame_duration(name, index, duration)
    old_frames = deepcopy(m.animations[name])
    old_ids = list(m.pose_ids[name])
    old_durations = list(m.frame_durations[name])
    m.parts[0]['x'] = 99
    assert m.insert_frame(name, 1) == 1
    assert len(m.animations[name]) == 4
    assert m.animations[name][0] == old_frames[0]
    assert m.animations[name][2:] == old_frames[1:]
    assert m.pose_ids[name][0] == old_ids[0]
    assert m.pose_ids[name][2:] == old_ids[1:]
    assert m.pose_ids[name][1] not in old_ids
    assert [m.frame_durations[name][i] for i in (0, 2, 3)] == old_durations
    m.animations[name][1][0]['x'] = 123
    assert m.animations[name][2:] == old_frames[1:]


def test_history_roundtrip_after_multiple_pose_edits_is_exact():
    m = PetSuiteModel()
    m.import_part('pixel', Image.new('RGBA', (2, 2), (20, 40, 60, 255)))
    history = EditHistory()
    initial = capture(m)
    history.record(m)
    m.parts[0]['x'] = 8
    after_first = capture(m)
    history.record(m)
    m.parts[0]['x'] = 16
    after_second = capture(m)
    assert history.undo(m) and capture(m) == after_first
    assert history.undo(m) and capture(m) == initial
    assert history.redo(m) and capture(m) == after_first
    assert history.redo(m) and capture(m) == after_second
