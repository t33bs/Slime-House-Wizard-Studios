"""Regression: pose navigation must not drive the hidden legacy recipe list."""
import ast
import pathlib
import unittest

SOURCE = pathlib.Path(__file__).resolve().parents[1] / 'friendly_animator.py'

class PoseNavigationContract(unittest.TestCase):
    def test_navigation_uses_saved_timeline(self):
        tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and any(isinstance(m, ast.FunctionDef) and m.name == 'prev_frame' for m in n.body))
        for method in ('prev_frame', 'next_frame'):
            node = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method)
            text = ast.unparse(node)
            self.assertIn('select_timeline_pose', text)
            self.assertIn('model.animations', text)
            self.assertNotIn('self.steps', text)

if __name__ == '__main__':
    unittest.main()
