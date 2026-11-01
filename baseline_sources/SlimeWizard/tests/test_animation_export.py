import tempfile
import unittest
from pathlib import Path
from PIL import Image
from studio.pet_suite_model import PetSuiteModel

class AnimationExportTests(unittest.TestCase):
    def sample(self):
        model=PetSuiteModel((32,32))
        model.import_part('paw',Image.new('RGBA',(5,5),(255,0,0,255)))
        first=model.snapshot()
        second=model.snapshot();second[0]['x']=10
        model.animations['Walking']=[first,second]
        model.set_frame_duration('Walking',0,100)
        model.set_frame_duration('Walking',1,250)
        return model
    def test_animated_files_and_durations(self):
        model=self.sample()
        with tempfile.TemporaryDirectory() as tmp:
            paths=model.export_animations(tmp)
            self.assertEqual(len(paths),2)
            for path in paths:
                self.assertTrue(path.exists())
                with Image.open(path) as image:
                    self.assertTrue(image.is_animated)
                    self.assertEqual(image.n_frames,2)
                    self.assertEqual(image.info['loop'],0)
                    self.assertEqual(image.info['duration'],100)
                    image.seek(1)
                    self.assertEqual(image.info['duration'],250)
    def test_dirty_fingerprint_and_save_roundtrip(self):
        model=self.sample();before=model.content_fingerprint()
        model.parts[0]['x']=2
        self.assertNotEqual(before,model.content_fingerprint())
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'pet.json';model.save_project(path)
            loaded=PetSuiteModel.load_project(path)
            self.assertEqual(model.content_fingerprint(),loaded.content_fingerprint())
    def test_no_frames_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):PetSuiteModel().export_animations(tmp)
