"""Regression checks for timeline mutation playback synchronization."""
import ast
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'friendly_animator.py'

class TimelineStructurePlaybackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        module = ast.parse(SOURCE.read_text())
        cls.methods = {node.name: node for item in module.body if isinstance(item, ast.ClassDef)
                       for node in item.body if isinstance(node, ast.FunctionDef)}

    def test_structural_mutations_rebase_preview(self):
        for name in ('duplicate_frame', 'insert_pose', 'import_pose_png', 'copy_pose', 'remove_pose', 'shift_pose'):
            with self.subTest(name=name):
                calls = [n for n in ast.walk(self.methods[name]) if isinstance(n, ast.Call)]
                self.assertTrue(any(isinstance(c.func, ast.Attribute) and c.func.attr == '_timeline_structure_changed' for c in calls))

    def test_rebase_uses_existing_playback_restart(self):
        calls = [n for n in ast.walk(self.methods['_timeline_structure_changed']) if isinstance(n, ast.Call)]
        self.assertTrue(any(isinstance(c.func, ast.Attribute) and c.func.attr == 'restart_playback' for c in calls))

if __name__ == '__main__':
    unittest.main()
