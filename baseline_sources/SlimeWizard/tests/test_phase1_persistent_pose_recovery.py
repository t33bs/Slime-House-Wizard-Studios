import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


class PersistentPoseRecoveryTests(unittest.TestCase):
    def make_model(self):
        m = PetSuiteModel()
        m.import_part('Swordcat', Image.new('RGBA', (4, 4), (0, 100, 255, 255)))
        m.save_frame('Idle')
        m.save_frame('Idle')
        return m

    def test_save_reload_restores_previous_version_without_neighbor_changes(self):
        m = self.make_model()
        first = m.pose_id('Idle', 0)
        second = m.pose_id('Idle', 1)
        before_neighbor = m.animations['Idle'][1].copy()
        m.edit_pose_at('Idle', 0, {0: {'x': 23}})
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'cat.rig.json'
            m.save_project(path)
            restored = PetSuiteModel.load_project(path)
            self.assertEqual(restored.pose_id('Idle', 0), first)
            self.assertEqual(restored.pose_id('Idle', 1), second)
            self.assertTrue(restored.restore_previous_pose('Idle', 0))
            self.assertEqual(restored.animations['Idle'][0][0]['x'], 0)
            self.assertEqual(restored.animations['Idle'][1], before_neighbor)

    def test_recovery_bound_and_orphan_cleanup_on_load(self):
        m = self.make_model()
        for x in range(1, 10):
            m.edit_pose_at('Idle', 0, {0: {'x': x}})
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'cat.rig.json'
            m.save_project(path)
            data = json.loads(path.read_text())
            data['pose_recovery']['orphaned-pose-id'] = [[{'x': 123}]]
            path.write_text(json.dumps(data))
            restored = PetSuiteModel.load_project(path)
            self.assertEqual(len(restored.pose_recovery[restored.pose_id('Idle', 0)]), 5)
            self.assertNotIn('orphaned-pose-id', restored.pose_recovery)

    def test_old_project_without_history_loads(self):
        m = self.make_model()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'cat.rig.json'
            m.save_project(path)
            data = json.loads(path.read_text())
            data.pop('pose_recovery')
            path.write_text(json.dumps(data))
            self.assertEqual(PetSuiteModel.load_project(path).pose_recovery, {})


if __name__ == '__main__':
    unittest.main()
