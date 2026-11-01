import unittest
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


class TestSlimerFrameRoundTrip(unittest.TestCase):
    def test_replace_only_selected_frame_and_reopen(self):
        import tempfile
        from pathlib import Path
        model=PetSuiteModel((16,16))
        red=Image.new('RGBA',(16,16),(255,0,0,255))
        model.import_part('base',red)
        model.insert_frame('Idle / Breathing',0)
        model.insert_frame('Idle / Breathing',1)
        before=model.render(model.animations['Idle / Breathing'][0]).tobytes()
        green=Image.new('RGBA',(16,16),(0,255,0,0))
        green.putpixel((5,5),(0,255,0,255))
        model.replace_frame_image('Idle / Breathing',1,green)
        poses=model.animations['Idle / Breathing']
        self.assertEqual(model.render(poses[0]).tobytes(),before)
        self.assertEqual(model.render(poses[1]).getpixel((5,5)),(0,255,0,255))
        self.assertEqual(model.render(poses[1]).getpixel((0,0)),(0,0,0,0))
        model.apply_pose(poses[0])
        self.assertFalse(model.parts[-1]['visible'])
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'creature.json'
            model.save_project(path)
            loaded=PetSuiteModel.load_project(path)
            saved=loaded.animations['Idle / Breathing']
            self.assertEqual(loaded.render(saved[0]).tobytes(),before)
            self.assertEqual(loaded.render(saved[1]).getpixel((5,5)),(0,255,0,255))

    def test_rejects_wrong_dimensions_without_changes(self):
        model=PetSuiteModel((16,16))
        model.import_part('base',Image.new('RGBA',(16,16)))
        model.insert_frame('Idle / Breathing',0)
        with self.assertRaises(ValueError):
            model.replace_frame_image('Idle / Breathing',0,Image.new('RGBA',(8,8)))
        self.assertEqual(len(model.parts),1)
