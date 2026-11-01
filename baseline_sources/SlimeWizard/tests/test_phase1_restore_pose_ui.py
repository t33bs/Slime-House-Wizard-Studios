import ast
import unittest
from pathlib import Path
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


class RestorePoseUIRegression(unittest.TestCase):
    def test_restore_button_is_wired_and_draft_is_not_resaved(self):
        source = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()
        tree = ast.parse(source)
        methods = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == 'restore_previous_timeline_pose']
        self.assertEqual(len(methods), 1)
        body = ast.get_source_segment(source, methods[0])
        self.assertIn('self._pose_draft_dirty = False', body)
        self.assertLess(body.index('self._pose_draft_dirty = False'), body.index('self.select_timeline_pose(index)'))
        self.assertIn('self.model.restore_previous_pose(name, index)', body)
        self.assertIn("('Restore Previous Pose',self.restore_previous_timeline_pose)", source)

    def test_restoring_selected_pose_preserves_neighbor_and_recovery_id(self):
        m = PetSuiteModel()
        m.import_part('Swordcat', Image.new('RGBA', (4, 4), 'blue'))
        m.save_frame('Idle')
        m.save_frame('Idle')
        neighbor = m.animations['Idle'][1].copy()
        pose_id = m.pose_id('Idle', 0)
        m.edit_pose_at('Idle', 0, {0: {'x': 17}})
        self.assertTrue(m.restore_previous_pose('Idle', 0))
        self.assertEqual(m.animations['Idle'][0][0]['x'], 0)
        self.assertEqual(m.animations['Idle'][1], neighbor)
        self.assertEqual(m.pose_id('Idle', 0), pose_id)

if __name__ == '__main__':
    unittest.main()
