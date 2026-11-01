"""Regression: recovery identities are unique across animation timelines."""
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


def test_duplicate_legacy_id_across_animations_is_repaired():
    m = PetSuiteModel((16, 16))
    m.import_part('cat', Image.new('RGBA', (16, 16), (1, 2, 3, 255)))
    m.insert_frame('Idle', 0)
    m.insert_frame('Walk', 0)
    duplicate = m.pose_id('Idle', 0)
    m.pose_ids['Walk'][0] = duplicate
    assert m.pose_id('Walk', 0) != duplicate
    assert m.pose_id('Idle', 0) == duplicate


def test_recovery_does_not_cross_animation_after_repair():
    m = PetSuiteModel((16, 16))
    m.import_part('cat', Image.new('RGBA', (16, 16), (1, 2, 3, 255)))
    m.insert_frame('Idle', 0)
    m.insert_frame('Walk', 0)
    m.pose_ids['Walk'][0] = m.pose_id('Idle', 0)
    m._sync_pose_ids('Walk')
    m.parts[0]['x'] = 2
    m.save_pose_at('Walk', 0)
    assert m.pose_id('Walk', 0) in m.pose_recovery
    assert m.pose_id('Idle', 0) not in m.pose_recovery
