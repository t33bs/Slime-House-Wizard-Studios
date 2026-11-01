from studio.pet_suite_model import PetSuiteModel


def test_drag_reorder_moves_pose_identity_and_duration_together():
    model = PetSuiteModel()
    name = 'Walking'
    for _ in range(4):
        model.insert_frame(name, len(model.animations.get(name, [])))
    model.frame_durations[name] = [100, 200, 300, 400]
    before = list(model.pose_ids[name])
    assert model.reorder_frame(name, 1, 3) == 3
    assert model.pose_ids[name] == [before[0], before[2], before[3], before[1]]
    assert model.frame_durations[name] == [100, 300, 400, 200]
    assert model.reorder_frame(name, 3, 0) == 0
    assert model.pose_ids[name] == [before[1], before[0], before[2], before[3]]
    assert model.frame_durations[name] == [200, 100, 300, 400]
