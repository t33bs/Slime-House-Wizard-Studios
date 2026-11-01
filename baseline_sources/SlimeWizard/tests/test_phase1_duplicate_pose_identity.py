import unittest
from pathlib import Path
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


class DuplicatePoseIdentityTests(unittest.TestCase):
    def test_duplicate_snapshot_keeps_old_ids_and_recovery(self):
        m = PetSuiteModel((8, 8))
        m.import_part('Swordcat', Image.new('RGBA', (2, 2), (10, 50, 90, 255)))
        m.save_frame('Idle')
        original_id = m.pose_id('Idle', 0)
        m.edit_pose_at('Idle', 0, {0: {'x': 3}})
        history = list(m.pose_recovery[original_id])
        index = m.insert_frame('Idle', len(m.animations['Idle']))
        self.assertEqual(index, 1)
        self.assertEqual(len(set(m.pose_ids['Idle'])), 2)
        self.assertEqual(m.pose_id('Idle', 0), original_id)
        self.assertEqual(m.pose_recovery[original_id], history)
        self.assertEqual(len(m.frame_durations['Idle']), 2)
        self.assertTrue(m.restore_previous_pose('Idle', 0))
        self.assertEqual(m.animations['Idle'][0][0]['x'], 0)
        self.assertEqual(m.animations['Idle'][1][0]['x'], 0)

    def test_gui_duplicate_uses_protected_insertion(self):
        source = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()
        block = source.split('    def duplicate_frame(self):', 1)[1].split('    def select_timeline_pose(', 1)[0]
        self.assertIn('self.model.copy_frame(name, source_index)', block)
        self.assertNotIn('poses.append(', block)
        self.assertIn('self.preserve_pose_draft()', block)


if __name__ == '__main__':
    unittest.main()
