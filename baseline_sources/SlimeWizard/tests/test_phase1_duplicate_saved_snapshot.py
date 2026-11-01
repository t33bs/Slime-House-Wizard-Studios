import unittest
from pathlib import Path
from studio.pet_suite_model import PetSuiteModel

SOURCE = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()

class DuplicateSavedSnapshotTests(unittest.TestCase):
    def test_gui_uses_saved_pose_not_working_canvas(self):
        block = SOURCE.split('    def duplicate_frame(self):', 1)[1].split('    def select_timeline_pose(self,index):', 1)[0]
        self.assertIn('self.model.copy_frame(name, source_index)', block)
        self.assertNotIn('self.model.insert_frame(', block)
        self.assertIn('self._pose_draft_key = None', block)

    def test_copy_frame_preserves_original_and_uses_independent_snapshot(self):
        model = PetSuiteModel()
        # Empty snapshots are sufficient to test identity and mutable isolation.
        model.animations['Idle'] = [[{'name': 'old', 'x': 3}], [{'name': 'new', 'x': 8}]]
        model._sync_pose_ids('Idle')
        original_id = model.pose_id('Idle', 0)
        second_id = model.pose_id('Idle', 1)
        copied_index = model.copy_frame('Idle', 0)
        self.assertEqual(copied_index, 1)
        self.assertEqual(model.animations['Idle'][1], model.animations['Idle'][0])
        self.assertNotEqual(model.pose_id('Idle', 1), original_id)
        self.assertEqual(model.pose_id('Idle', 2), second_id)
        model.animations['Idle'][1][0]['x'] = 999
        self.assertEqual(model.animations['Idle'][0][0]['x'], 3)
        self.assertEqual(model.animations['Idle'][2][0]['x'], 8)

if __name__ == '__main__': unittest.main()
