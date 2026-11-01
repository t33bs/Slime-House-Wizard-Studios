"""Guard older frame pixels when a new working pose is created after Slimer-like edits."""
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


def test_older_pose_source_pngs_unchanged_when_new_assets_are_added(tmp_path):
    m = PetSuiteModel((256, 256))
    art = Image.new('RGBA', m.size)
    art.putpixel((30, 40), (255, 255, 255, 255))
    art.putpixel((65, 94), (0, 0, 0, 255))
    art.putpixel((110, 72), (30, 120, 40, 133))
    m.import_part('Cat', art)
    name = m.current
    m.insert_frame(name, 0)
    first_saved = m.animations[name][0][0]['source_png']
    first_rgba = m.render(m.animations[name][0]).tobytes()

    m.apply_pose(m.animations[name][0])
    m.parts[0]['x'] = 3
    m.save_pose_at(name, 0)
    first_pose = m.render(m.animations[name][0]).tobytes()
    second = m.merged_working_pose(m.animations[name][0], 'Combined Artwork 002')
    m.insert_frame(name, 1, second)
    m.apply_pose(m.animations[name][1])
    m.parts[1]['x'] = 2
    m.save_pose_at(name, 1)
    second_pose = m.render(m.animations[name][1]).tobytes()
    assert second_pose != first_pose

    third = m.merged_working_pose(m.animations[name][1], 'Combined Artwork 003')
    m.insert_frame(name, 2, third)
    assert m.animations[name][0][0]['source_png'] == first_saved
    assert m.render(m.animations[name][0]).tobytes() == first_pose
    assert m.render(m.animations[name][1]).tobytes() == second_pose
    m.apply_pose(m.animations[name][0])
    assert m.render().tobytes() == first_pose
    m.apply_pose(m.animations[name][1])
    assert m.render().tobytes() == second_pose

    path = tmp_path / 'walk.rig.json'
    m.save_project(path)
    loaded = PetSuiteModel.load_project(path)
    assert loaded.render(loaded.animations[name][0]).tobytes() == first_pose
    assert loaded.render(loaded.animations[name][1]).tobytes() == second_pose
    assert first_rgba != first_pose
