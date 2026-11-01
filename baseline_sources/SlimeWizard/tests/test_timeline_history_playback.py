"""Guard playback synchronization on timeline undo/redo without Qt dependency."""
import ast
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'friendly_animator.py'

class TimelineHistoryPlaybackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        module = ast.parse(SOURCE.read_text())
        cls.methods = {node.name: node for item in module.body if isinstance(item, ast.ClassDef)
                       for node in item.body if isinstance(node, ast.FunctionDef)}

    def test_undo_redo_use_structural_history_sync(self):
        for name in ('undo', 'redo'):
            with self.subTest(name=name):
                calls = [n.func.attr for n in ast.walk(self.methods[name])
                         if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)]
                self.assertIn('_timeline_history_signature', calls)
                self.assertIn('_after_history_restore', calls)

    def test_rebase_only_on_timeline_change(self):
        method = self.methods['_after_history_restore']
        conditions = [n for n in ast.walk(method) if isinstance(n, ast.If)]
        self.assertTrue(any(any(isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                                and c.func.attr == '_timeline_history_signature' for c in ast.walk(n.test))
                            for n in conditions))
        self.assertTrue(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                            and n.func.attr == '_timeline_structure_changed' for n in ast.walk(method)))

if __name__ == '__main__':
    unittest.main()
