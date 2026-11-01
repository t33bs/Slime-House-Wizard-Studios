"""Headless checks of pose UI wiring; real Windows GUI verification remains required."""
import ast
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'friendly_animator.py'

class Phase2PoseUIContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
        cls.methods = {n.name: n for c in cls.tree.body if isinstance(c, ast.ClassDef) for n in c.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}

    def test_save_current_pose_uses_targeted_model_save(self):
        method = self.methods['save_frame']
        calls = [n for n in ast.walk(method) if isinstance(n, ast.Call)]
        self.assertTrue(any(isinstance(c.func, ast.Attribute) and c.func.attr == 'save_pose_at' for c in calls))
        self.assertFalse(any(isinstance(c.func, ast.Attribute) and c.func.attr in ('append','insert_frame') for c in calls))

    def test_select_pose_explicitly_loads_even_if_row_unchanged(self):
        method = self.methods['select_timeline_pose']
        self.assertTrue(any(isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr == 'load_frame' for c in ast.walk(method)))

    def test_place_frame_does_not_require_slimer_selection(self):
        method = self.methods['slimer_place_frame']
        self.assertTrue(any(isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute) and c.func.attr == 'insert_frame' for c in ast.walk(method)))

if __name__ == '__main__':
    unittest.main()
