import tempfile
import unittest
from pathlib import Path
from studio.pet_suite_model import PetSuiteModel
from studio.recovery import (write_project_recovery, list_project_recoveries,
    discard_project_recovery, read_recovery)

class MultiRecoveryTests(unittest.TestCase):
    def test_separate_snapshots_and_discard(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            a=PetSuiteModel();b=PetSuiteModel()
            pa=write_project_recovery(a,0,root)
            pb=write_project_recovery(b,1,root)
            self.assertNotEqual(pa,pb)
            self.assertEqual(list_project_recoveries(root),[pa,pb])
            self.assertIsInstance(read_recovery(pa),PetSuiteModel)
            discard_project_recovery(0,root)
            self.assertEqual(list_project_recoveries(root),[pb])
    def test_invalid_id(self):
        with self.assertRaises(ValueError):write_project_recovery(PetSuiteModel(),-1)
