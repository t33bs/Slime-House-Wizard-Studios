"""End-to-end model regressions for timeline isolation; GUI checks remain deferred."""
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


def test_pose_reorder_duplicate_edit_restore_keeps_neighbor_pixels():
    m = PetSuiteModel((24, 24))
    img = Image.new('RGBA', (24, 24))
    img.putpixel((3, 3), (100, 140, 200, 128))
    m.import_part('pixel', img)
    for x in (0, 4, 8):
        m.parts[0]['x'] = x
        m.insert_frame('Walk', len(m.animations.get('Walk', [])))
    originals = {m.pose_id('Walk', i): m.render(p).tobytes() for i, p in enumerate(m.animations['Walk'])}
    m.move_frame('Walk', 0, 1)
    for i, p in enumerate(m.animations['Walk']):
        assert m.render(p).tobytes() == originals[m.pose_id('Walk', i)]
    copied_index = m.copy_frame('Walk', 1)
    assert m.pose_id('Walk', copied_index) not in originals
    assert m.render(m.animations['Walk'][copied_index]).tobytes() == originals[m.pose_id('Walk', 1)]
    m.edit_pose_at('Walk', copied_index, {0: {'x': 12}})
    assert m.restore_previous_pose('Walk', copied_index)
    assert m.render(m.animations['Walk'][copied_index]).tobytes() == originals[m.pose_id('Walk', 1)]
    for i, p in enumerate(m.animations['Walk']):
        if m.pose_id('Walk', i) in originals:
            assert m.render(p).tobytes() == originals[m.pose_id('Walk', i)]


def test_pose_ids_are_unique_across_many_animations_and_changes():
    m = PetSuiteModel((8, 8))
    m.import_part('pixel', Image.new('RGBA', (8, 8), (10, 20, 30, 128)))
    for name in ('Idle', 'Walk', 'Attack', 'Sleep'):
        for i in range(6):
            m.parts[0]['x'] = i
            m.insert_frame(name, i)
        m.copy_frame(name, 2)
        m.move_frame(name, 0, 1)
        m.delete_frame(name, 3)
    ids = [m.pose_id(name, i) for name, frames in m.animations.items() for i in range(len(frames))]
    assert len(ids) == len(set(ids))
