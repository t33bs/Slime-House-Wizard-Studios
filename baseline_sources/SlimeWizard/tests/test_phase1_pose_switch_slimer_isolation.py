import unittest
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()

class PoseSwitchIsolationContract(unittest.TestCase):
    def test_pose_switch_compares_project_animation_and_index(self):
        self.assertIn('next_key=self._saved_pose_key(animation,index)', SOURCE)
        self.assertIn('changing_pose=previous_key is not None and previous_key != next_key', SOURCE)

    def test_selection_reset_happens_after_new_pose_is_applied(self):
        block = SOURCE.split('    def load_frame(self,index):', 1)[1].split('    def save_frame(self):', 1)[0]
        self.assertLess(block.index('self._apply_saved_pose(animation,index)'), block.index('self._reset_slimer_for_project_change()'))
        self.assertIn('if changing_pose:', block)

if __name__ == '__main__':
    unittest.main()
