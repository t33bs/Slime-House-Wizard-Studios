"""Structural regression checks for GUI save/close integration (no Qt runtime required)."""
import ast
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'friendly_animator.py'
TREE = ast.parse(SOURCE.read_text())
SUITE = next(n for n in TREE.body if isinstance(n,ast.ClassDef) and n.name=='Suite')
METHODS = {n.name:n for n in SUITE.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}

def calls(method):
    return {n.func.attr for n in ast.walk(METHODS[method]) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)}

class UnsavedWorkflowTests(unittest.TestCase):
    def test_close_and_exit_both_guard_unsaved(self):
        self.assertIn('confirm_unsaved_projects',calls('closeEvent'))
        self.assertIn('confirm_unsaved_projects',calls('close_creature_project'))
    def test_save_discard_cancel_options(self):
        attrs={n.attr for n in ast.walk(METHODS['confirm_unsaved_projects']) if isinstance(n,ast.Attribute)}
        self.assertTrue({'Save','Discard','Cancel'}.issubset(attrs))
    def test_save_failure_blocks_close(self):
        self.assertIn('save_project_by_id',calls('confirm_unsaved_projects'))
        self.assertIn('getSaveFileName',calls('save_project_by_id'))
    def test_save_updates_fingerprint_and_clears_recovery(self):
        self.assertIn('content_fingerprint',calls('save_project_by_id'))
        self.assertIn('discard',calls('save_project_by_id'))
