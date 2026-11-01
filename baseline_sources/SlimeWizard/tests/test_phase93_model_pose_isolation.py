"""Headless stable pose identity and RGB/alpha preservation across frames."""
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


def test_three_distinct_saved_poses_do_not_overwrite_one_another(tmp_path):
    model = PetSuiteModel()
    name = model.current
    sprite = Image.new('RGBA', model.size)
    sprite.putpixel((12,18), (0,0,0,255))
    sprite.putpixel((53,65), (100,120,140,136))
    model.import_part('Base', sprite)
    model.insert_frame(name,0)
    first_id = model.pose_id(name,0)
    model.parts[0]['x'] = 3
    model.save_pose_at(name,0)
    first = model.render(model.animations[name][0]).tobytes()
    second_source = model.merged_working_pose(model.animations[name][0], 'Combined Artwork 002')
    model.insert_frame(name,1,second_source)
    second_id = model.pose_id(name,1)
    model.apply_pose(model.animations[name][1])
    # Pose 2 moves only its composite layer and saves independently.
    model.parts[1]['x'] = 7
    model.save_pose_at(name,1)
    second = model.render(model.animations[name][1]).tobytes()
    assert second != first
    third_source = model.merged_working_pose(model.animations[name][1], 'Combined Artwork 003')
    model.insert_frame(name,2,third_source)
    assert model.render(model.animations[name][0]).tobytes() == first
    assert model.render(model.animations[name][1]).tobytes() == second
    assert model.render(model.animations[name][2]).tobytes() == second
    assert model.pose_ids[name][:2] == [first_id,second_id]
    path = tmp_path / 'poses.slime'
    model.save_project(path)
    reopened = PetSuiteModel.load_project(path)
    assert reopened.render(reopened.animations[name][0]).tobytes() == first
    assert reopened.render(reopened.animations[name][1]).tobytes() == second
    assert reopened.render(reopened.animations[name][2]).tobytes() == second
    assert reopened.pose_ids[name][:2] == [first_id,second_id]
