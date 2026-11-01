import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from studio.pet_suite_model import PetSuiteModel
from studio.recovery import write_recovery, read_recovery, list_project_recoveries

class RecoveryHardeningTests(unittest.TestCase):
    def test_repeated_snapshots_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'creature_1.rig.json'
            model=PetSuiteModel()
            write_recovery(model,path)
            write_recovery(model,path)
            self.assertIsInstance(read_recovery(path),PetSuiteModel)
            self.assertEqual(list_project_recoveries(tmp),[path])

    def test_failed_staging_preserves_previous(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'creature_2.rig.json'
            model=PetSuiteModel()
            write_recovery(model,path)
            previous=path.read_bytes()
            with patch.object(PetSuiteModel,'save_project',side_effect=OSError('disk full')):
                with self.assertRaises(OSError):write_recovery(model,path)
            self.assertEqual(path.read_bytes(),previous)
            self.assertIsInstance(read_recovery(path),PetSuiteModel)

    def test_no_staging_left_after_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'creature_3.rig.json'
            with patch.object(PetSuiteModel,'save_project',side_effect=OSError('disk full')):
                with self.assertRaises(OSError):write_recovery(PetSuiteModel(),path)
            self.assertFalse(list(Path(tmp).glob('_staging_*')))
