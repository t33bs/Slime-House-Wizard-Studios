import unittest
from pathlib import Path
SOURCE=(Path(__file__).resolve().parents[1]/'friendly_animator.py').read_text()

class AnimationStepIsolationContract(unittest.TestCase):
    def test_animation_switch_resets_transient_slimer_even_when_empty(self):
        block=SOURCE.split('    def change_anim(self,name):',1)[1].split('    def select_step(self,index):',1)[0]
        self.assertIn('previous_animation=self.model.current',block)
        self.assertIn('if previous_animation != name:',block)
        self.assertIn('self._reset_slimer_for_project_change()',block)
    def test_step_switch_resets_after_destination_pose_loaded(self):
        block=SOURCE.split('    def select_step(self,index):',1)[1].split('    def sync_slimer_asset_labels(self):',1)[0]
        self.assertIn('changing_pose=previous_key is not None and previous_key != next_key',block)
        self.assertLess(block.index('self._apply_saved_pose(animation,index)'),block.index('self._reset_slimer_for_project_change()'))
        self.assertIn('if changing_pose:',block)

if __name__=='__main__':unittest.main()
