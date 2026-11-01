import unittest
from PIL import Image
from studio.pet_suite_model import PetSuiteModel

class RenderRGBARegression(unittest.TestCase):
    def test_single_semitransparent_pixel_preserves_alpha(self):
        model = PetSuiteModel((8, 8))
        source = Image.new('RGBA', (8, 8), (0, 0, 0, 0))
        source.putpixel((2, 3), (17, 99, 233, 128))
        model.import_part('partial', source)
        for _ in range(10):
            self.assertEqual(model.render().getpixel((2, 3)), (17, 99, 233, 128))

    def test_saved_pose_render_is_independent_of_active_pose(self):
        model = PetSuiteModel((8, 8))
        source = Image.new('RGBA', (8, 8), (50, 100, 150, 128))
        model.import_part('partial', source)
        model.insert_frame('Idle', 0)
        expected = model.render(model.animations['Idle'][0]).tobytes()
        model.parts[0]['x'] = 2
        model.insert_frame('Idle', 1)
        for _ in range(10):
            self.assertEqual(model.render(model.animations['Idle'][0]).tobytes(), expected)

if __name__ == '__main__': unittest.main()
