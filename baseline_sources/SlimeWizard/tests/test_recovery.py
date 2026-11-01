import tempfile
import unittest
from pathlib import Path
from PIL import Image
from studio.pet_suite_model import PetSuiteModel
from studio.recovery import write_recovery, read_recovery, discard_recovery

class RecoveryTests(unittest.TestCase):
    def test_round_trip_and_replace(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'recovery.rig.json'
            model=PetSuiteModel();model.import_part('head',Image.new('RGBA',(8,8),'red'))
            write_recovery(model,path)
            self.assertEqual(len(read_recovery(path).parts),1)
            model.import_part('tail',Image.new('RGBA',(4,4),'blue'))
            write_recovery(model,path)
            self.assertEqual(len(read_recovery(path).parts),2)
            discard_recovery(path)
            self.assertFalse(path.exists())
            self.assertFalse(path.with_suffix('').exists())
