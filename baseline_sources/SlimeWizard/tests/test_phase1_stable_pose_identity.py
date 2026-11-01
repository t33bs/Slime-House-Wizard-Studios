import tempfile
import unittest
from pathlib import Path
from PIL import Image
from studio.pet_suite_model import PetSuiteModel

class StablePoseIdentityTests(unittest.TestCase):
    def setUp(self):
        self.m = PetSuiteModel((8, 8))
        self.m.import_part('Swordcat', Image.new('RGBA', (2, 2), (30, 90, 210, 255)))
        for x in (0, 2, 4):
            self.m.parts[0]['x'] = x
            self.m.save_frame('Idle')

    def test_move_keeps_recovery_with_artwork(self):
        m = self.m
        target_id = m.pose_id('Idle', 1)
        m.edit_pose_at('Idle', 1, {0: {'x': 3}})
        m.move_frame('Idle', 1, 1)
        self.assertEqual(m.pose_id('Idle', 2), target_id)
        self.assertTrue(m.restore_previous_pose('Idle', 2))
        self.assertEqual(m.animations['Idle'][2][0]['x'], 2)
        self.assertEqual(m.animations['Idle'][1][0]['x'], 4)

    def test_insert_does_not_steal_recovery(self):
        m = self.m
        target_id = m.pose_id('Idle', 1)
        m.edit_pose_at('Idle', 1, {0: {'x': 7}})
        m.insert_frame('Idle', 0)
        self.assertEqual(m.pose_id('Idle', 2), target_id)
        self.assertTrue(m.restore_previous_pose('Idle', 2))
        self.assertEqual(m.animations['Idle'][2][0]['x'], 2)

    def test_delete_does_not_steal_neighbor_recovery(self):
        m = self.m
        kept_id = m.pose_id('Idle', 2)
        removed_id = m.pose_id('Idle', 1)
        m.edit_pose_at('Idle', 1, {0: {'x': 6}})
        m.edit_pose_at('Idle', 2, {0: {'x': 5}})
        m.delete_frame('Idle', 1)
        self.assertEqual(m.pose_id('Idle', 1), kept_id)
        self.assertNotIn(removed_id, m.pose_recovery)
        self.assertTrue(m.restore_previous_pose('Idle', 1))
        self.assertEqual(m.animations['Idle'][1][0]['x'], 4)

    def test_project_roundtrip_preserves_ids(self):
        m = self.m
        ids = list(m.pose_ids['Idle'])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'creature.json'
            m.save_project(path)
            loaded = PetSuiteModel.load_project(path)
            self.assertEqual(loaded.pose_ids['Idle'], ids)
            self.assertEqual(loaded.animations, m.animations)

    def test_legacy_project_assigns_unique_ids(self):
        m = self.m
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'creature.json'
            m.save_project(path)
            import json
            data = json.loads(path.read_text())
            data.pop('pose_ids')
            path.write_text(json.dumps(data))
            loaded = PetSuiteModel.load_project(path)
            self.assertEqual(len(set(loaded.pose_ids['Idle'])), 3)

if __name__ == '__main__':
    unittest.main()
