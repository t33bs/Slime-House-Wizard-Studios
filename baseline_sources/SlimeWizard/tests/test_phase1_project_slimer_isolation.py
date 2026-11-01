"""Source-level regression contract for active Slimer during New Creature.

GUI behavior still requires a Windows/PySide6 integration test.
"""
import ast
import unittest
from pathlib import Path

SOURCE=Path(__file__).resolve().parents[1] / 'friendly_animator.py'
TREE=ast.parse(SOURCE.read_text())

def method(name):
    return next(n for n in ast.walk(TREE) if isinstance(n,ast.FunctionDef) and n.name==name)

class ProjectSlimerIsolationTests(unittest.TestCase):
    def test_new_creature_uses_project_activation(self):
        body=ast.get_source_segment(SOURCE.read_text(),method('new_project'))
        self.assertIn('self.add_project(',body)
        self.assertIn('PetSuiteModel((width, height))',body)
        body=ast.get_source_segment(SOURCE.read_text(),method('add_project'))
        self.assertIn('self.select_workspace_key(key)',body)

    def test_project_activation_resets_selection_after_switching_model(self):
        body=ast.get_source_segment(SOURCE.read_text(),method('activate_project'))
        self.assertLess(body.index('self.model=self._projects[project_id]'),body.index('self._reset_slimer_for_project_change()'))

    def test_reset_is_transient_only_and_rebinds_selection_to_current_render(self):
        body=ast.get_source_segment(SOURCE.read_text(),method('_reset_slimer_for_project_change'))
        for token in ('self.slimer_phase_masks={}', 'self.canvas._slimer_last=None',
                      'self.canvas.slimer_bounds=None','self.slimer_selection_undo.clear()',
                      'SlimerSelection.empty(self.model.render())'):
            self.assertIn(token,body)
        for forbidden in ('self.model.parts.clear(', 'self.model.animations.clear(',
                          'self.model.originals.clear(', 'self.slimer_toggle.setChecked(False)'):
            self.assertNotIn(forbidden,body)

if __name__=='__main__': unittest.main()
