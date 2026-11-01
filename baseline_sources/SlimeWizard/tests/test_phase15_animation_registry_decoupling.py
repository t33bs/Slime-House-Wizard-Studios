import unittest
from types import SimpleNamespace
from studio.animation_registry import available_animation_names, preferred_animation

class AnimationRegistryTests(unittest.TestCase):
    def test_preserves_custom_saved_animation_names(self):
        model = SimpleNamespace(current='My Custom Dance', animations={'My Custom Dance': [object()], 'Walking': []})
        names = available_animation_names(model)
        self.assertIn('My Custom Dance', names)
        self.assertIn('Walking', names)
        self.assertEqual(preferred_animation(model, 'My Custom Dance'), 'My Custom Dance')

    def test_unknown_requested_name_falls_back_to_current(self):
        model = SimpleNamespace(current='My Special Pose', animations={})
        self.assertEqual(preferred_animation(model, 'missing'), 'My Special Pose')

    def test_names_do_not_depend_on_recipe_modules(self):
        import inspect
        import studio.animation_registry as registry
        self.assertNotIn('pet_suite_templates', inspect.getsource(registry))
        self.assertNotIn('reference_animation', inspect.getsource(registry))

if __name__ == '__main__': unittest.main()
