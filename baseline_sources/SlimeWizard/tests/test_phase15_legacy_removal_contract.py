"""Guardrails against reintroducing removed recipe machinery."""
from pathlib import Path
import unittest
from studio.animation_registry import available_animation_names
from studio.resource_checks import bundled_resource_report

ROOT = Path(__file__).resolve().parents[1]

class LegacyRemovalContract(unittest.TestCase):
    def test_obsolete_recipe_modules_absent(self):
        for name in ('pet_suite_templates.py', 'reference_animation.py', 'pose_guidance.py'):
            self.assertFalse((ROOT / 'studio' / name).exists(), name)

    def test_retained_resource_check_is_clean(self):
        self.assertEqual([], bundled_resource_report())

    def test_no_reference_image_viewer_or_loader(self):
        source = (ROOT / 'friendly_animator.py').read_text(encoding='utf-8')
        for symbol in ('load_uploaded_reference', 'render_uploaded_reference',
                       'uploaded_reference_toggle', 'reference_files'):
            self.assertNotIn(symbol, source)
        self.assertFalse((ROOT / 'studio' / 'user_reference.py').exists())
        self.assertFalse((ROOT / 'studio' / 'comparison_sync.py').exists())

    def test_active_code_has_no_recipe_module_imports(self):
        import ast
        for file in (ROOT / 'friendly_animator.py', *(ROOT / 'studio').glob('*.py')):
            tree = ast.parse(file.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    modules = [node.module or '']
                else:
                    continue
                for module in modules:
                    self.assertFalse(any(module.endswith(name) for name in
                        ('pet_suite_templates', 'reference_animation', 'pose_guidance')),
                        f'{file.name}: obsolete import {module}')

    def test_old_recipe_controls_not_reintroduced(self):
        source = (ROOT / 'friendly_animator.py').read_text(encoding='utf-8')
        for obsolete in ('self.recipe_toggle', 'self.recipe_steps', 'self.follow_recipe',
                         'Follow Recipe', 'generated reference animation'):
            self.assertNotIn(obsolete, source)

    def test_animation_names_work_without_recipes(self):
        class Model:
            animations = {'My Custom Animation': []}
            current = 'My Custom Animation'
        self.assertIn('My Custom Animation', available_animation_names(Model()))

if __name__ == '__main__':
    unittest.main()
