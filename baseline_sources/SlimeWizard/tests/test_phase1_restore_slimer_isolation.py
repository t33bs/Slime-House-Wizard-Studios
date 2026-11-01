"""Regression coverage for stale selection after pose recovery."""
import ast
import unittest
from pathlib import Path

from studio.pet_suite_model import PetSuiteModel
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

class RestoreSlimerIsolationTests(unittest.TestCase):
    def test_restore_rebinds_slimer_after_loading_recovered_pose(self):
        tree = ast.parse((ROOT / 'friendly_animator.py').read_text(encoding='utf-8'))
        methods = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'restore_previous_timeline_pose']
        self.assertEqual(len(methods), 1)
        calls = [n for n in ast.walk(methods[0]) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) and n.func.value.id == 'self']
        names = [n.func.attr for n in calls]
        self.assertLess(names.index('select_timeline_pose'), names.index('_reset_slimer_for_project_change'))
        self.assertLess(names.index('_reset_slimer_for_project_change'), names.index('refresh'))

    def test_restore_changes_only_selected_pose(self):
        m = PetSuiteModel((8, 8))
        m.import_part('sample', Image.new('RGBA', (4, 4), (255, 0, 0, 255)))
        m.insert_frame('Idle', 0)
        m.insert_frame('Idle', 1)
        other = m.animations['Idle'][1]
        m.parts[0]['x'] = 20
        m.save_pose_at('Idle', 0)
        self.assertTrue(m.restore_previous_pose('Idle', 0))
        self.assertEqual(m.animations['Idle'][0][0]['x'], 0)
        self.assertEqual(m.animations['Idle'][1], other)

if __name__ == '__main__': unittest.main()
