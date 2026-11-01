"""Phase 15 regression: saving and editing a pose cannot mutate its neighbors."""
import unittest
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


class SavedPoseIsolationTests(unittest.TestCase):
    def test_reedit_middle_pose_preserves_neighbor_source_pixels(self):
        model = PetSuiteModel()
        source = Image.new('RGBA', (128, 128))
        source.putpixel((4, 4), (255, 0, 0, 255))
        model.import_part('body', source)
        animation = 'Idle / Breathing'
        for x in (0, 3, 6):
            model.parts[0]['x'] = x
            model.insert_frame(animation, len(model.animations.get(animation, [])))
        before_first = model.render(model.animations[animation][0]).tobytes()
        before_last = model.render(model.animations[animation][2]).tobytes()
        model.apply_pose(model.animations[animation][1])
        model.parts[0]['x'] = 9
        model.save_pose_at(animation, 1)
        self.assertEqual(model.animations[animation][1][0]['x'], 9)
        self.assertEqual(model.render(model.animations[animation][0]).tobytes(), before_first)
        self.assertEqual(model.render(model.animations[animation][2]).tobytes(), before_last)
        model.parts[0]['image'].putpixel((4, 4), (0, 0, 0, 0))
        self.assertEqual(model.render(model.animations[animation][0]).tobytes(), before_first)
        self.assertEqual(model.render(model.animations[animation][2]).tobytes(), before_last)

    def test_saved_pose_reedit_does_not_add_timeline_frame(self):
        model = PetSuiteModel()
        model.import_part('body', Image.new('RGBA', (128, 128), (255, 0, 0, 255)))
        animation = 'Idle / Breathing'
        model.insert_frame(animation, 0)
        count = len(model.animations[animation])
        model.parts[0]['visible'] = False
        model.save_pose_at(animation, 0)
        self.assertEqual(len(model.animations[animation]), count)
        self.assertFalse(model.animations[animation][0][0]['visible'])


if __name__ == '__main__':
    unittest.main()
