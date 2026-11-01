import unittest
from PIL import Image
from studio.pet_suite_model import PetSuiteModel

class PoseRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.model = PetSuiteModel((8, 8))
        self.model.import_part('body', Image.new('RGBA', (8, 8), (255, 0, 0, 255)))
        self.model.insert_frame('Idle', 0)
        self.model.insert_frame('Idle', 1)

    def test_save_restores_previous_without_touching_neighbor(self):
        m = self.model
        before = m.render(m.animations['Idle'][0]).tobytes()
        neighbor = m.render(m.animations['Idle'][1]).tobytes()
        m.parts[0]['x'] = 2
        m.save_pose_at('Idle', 0)
        self.assertNotEqual(before, m.render(m.animations['Idle'][0]).tobytes())
        self.assertTrue(m.restore_previous_pose('Idle', 0))
        self.assertEqual(before, m.render(m.animations['Idle'][0]).tobytes())
        self.assertEqual(neighbor, m.render(m.animations['Idle'][1]).tobytes())

    def test_unchanged_save_does_not_add_recovery(self):
        m = self.model
        m.save_pose_at('Idle', 0)
        self.assertFalse(m.pose_recovery)

    def test_recovery_is_bounded(self):
        m = self.model
        for i in range(12):
            m.parts[0]['x'] = i + 1
            m.save_pose_at('Idle', 0)
        self.assertEqual(len(m.pose_recovery[m.pose_id('Idle', 0)]), 5)

if __name__ == '__main__':
    unittest.main()
