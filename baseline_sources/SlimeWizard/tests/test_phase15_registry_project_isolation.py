"""Recipe-free selector must not leak names or mutate saved project state."""
import unittest
from studio.animation_registry import available_animation_names, preferred_animation
from studio.pet_suite_model import PetSuiteModel


class RegistryIsolationTests(unittest.TestCase):
    def test_switching_models_does_not_leak_custom_names(self):
        first = PetSuiteModel()
        first.animations['Creature A Dance'] = [first.snapshot()]
        first.current = 'Creature A Dance'
        second = PetSuiteModel()
        second.animations['Creature B Wiggle'] = [second.snapshot()]
        second.current = 'Creature B Wiggle'
        before_a = first.content_fingerprint()
        before_b = second.content_fingerprint()
        self.assertIn('Creature A Dance', available_animation_names(first))
        self.assertNotIn('Creature A Dance', available_animation_names(second))
        self.assertIn('Creature B Wiggle', available_animation_names(second))
        self.assertNotIn('Creature B Wiggle', available_animation_names(first))
        self.assertEqual(preferred_animation(first), 'Creature A Dance')
        self.assertEqual(preferred_animation(second), 'Creature B Wiggle')
        self.assertEqual(first.content_fingerprint(), before_a)
        self.assertEqual(second.content_fingerprint(), before_b)

    def test_selector_is_deduplicated_and_nonmutating(self):
        model = PetSuiteModel()
        model.animations['Walking'] = [model.snapshot()]
        model.animations['Custom'] = [model.snapshot()]
        model.animations['Custom Creature Action'] = [model.snapshot()]
        model.current = 'Custom Creature Action'
        before = model.content_fingerprint()
        names = available_animation_names(model)
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(names.count('Walking'), 1)
        self.assertEqual(names.count('Custom'), 1)
        self.assertEqual(names.count('Custom Creature Action'), 1)
        self.assertEqual(model.content_fingerprint(), before)


if __name__ == '__main__':
    unittest.main()
