"""Legacy recipe labels are project data, not instructions or generated frames."""
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from studio.pet_suite_model import PetSuiteModel
from studio.animation_registry import available_animation_names, preferred_animation


class LegacyProjectCompatibilityTests(unittest.TestCase):
    def test_legacy_label_and_custom_animation_survive_roundtrip(self):
        model = PetSuiteModel((16, 16))
        pixel = Image.new('RGBA', (2, 2), (120, 40, 200, 255))
        model.import_part('Nonstandard creature part', pixel)
        model.animations['Pooping'] = [model.snapshot()]
        model.animations['My Unusual Dance'] = [model.snapshot()]
        model.current = 'My Unusual Dance'
        model.set_frame_duration('Pooping', 0, 275)
        model.set_frame_duration('My Unusual Dance', 0, 425)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'old_project.json'
            model.save_project(path)
            reopened = PetSuiteModel.load_project(path)
            self.assertEqual(reopened.current, 'My Unusual Dance')
            self.assertEqual(list(reopened.animations), ['Pooping', 'My Unusual Dance'])
            self.assertEqual(reopened.frame_durations['Pooping'], [275])
            self.assertEqual(reopened.frame_durations['My Unusual Dance'], [425])
            self.assertIn('Pooping', available_animation_names(reopened))
            self.assertIn('My Unusual Dance', available_animation_names(reopened))
            self.assertEqual(preferred_animation(reopened, 'My Unusual Dance'), 'My Unusual Dance')
            self.assertEqual(reopened.render(reopened.animations['Pooping'][0]).tobytes(),
                             model.render(model.animations['Pooping'][0]).tobytes())
            sheet = reopened.export(Path(tmp) / 'out', basename='legacy')
            metadata = json.loads(sheet.with_suffix('.json').read_text())
            self.assertEqual([(f['animation'], f['duration_ms']) for f in metadata['frames']],
                             [('Pooping', 275), ('My Unusual Dance', 425)])

    def test_current_name_without_saved_frames_remains_selectable(self):
        model = PetSuiteModel()
        model.current = 'Historical Custom Name'
        self.assertEqual(preferred_animation(model), 'Historical Custom Name')
        self.assertIn('Historical Custom Name', available_animation_names(model))

if __name__ == '__main__':
    unittest.main()
