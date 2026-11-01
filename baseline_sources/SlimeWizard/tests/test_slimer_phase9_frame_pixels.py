import tempfile
import unittest
from pathlib import Path
from PIL import Image
from studio.pet_suite_model import PetSuiteModel

class Phase9FramePixels(unittest.TestCase):
    def test_previous_pose_preserves_pixels_after_source_erase_and_new_pose(self):
        model=PetSuiteModel((16,16))
        art=Image.new('RGBA',(16,16))
        art.putpixel((3,3),(255,0,0,255))
        model.import_part('arm',art)
        model.insert_frame('Idle',0)
        moved=Image.new('RGBA',(16,16))
        moved.putpixel((3,7),(255,0,0,255))
        model.originals[0]=moved.copy()
        model.parts[0]['image']=moved.copy()
        model.insert_frame('Idle',1)
        self.assertEqual(model.render(model.animations['Idle'][0]).getpixel((3,3)),(255,0,0,255))
        self.assertEqual(model.render(model.animations['Idle'][0]).getpixel((3,7))[3],0)
        self.assertEqual(model.render(model.animations['Idle'][1]).getpixel((3,3))[3],0)
        self.assertEqual(model.render(model.animations['Idle'][1]).getpixel((3,7)),(255,0,0,255))
        model.apply_pose(model.animations['Idle'][0])
        self.assertEqual(model.render().getpixel((3,3)),(255,0,0,255))
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'cat.json'
            model.save_project(path)
            restored=PetSuiteModel.load_project(path)
            self.assertEqual(restored.render(restored.animations['Idle'][0]).getpixel((3,3)),(255,0,0,255))
            self.assertEqual(restored.render(restored.animations['Idle'][1]).getpixel((3,7)),(255,0,0,255))
