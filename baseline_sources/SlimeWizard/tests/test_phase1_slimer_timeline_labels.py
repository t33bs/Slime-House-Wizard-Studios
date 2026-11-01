"""Regression checks for timeline-indexed Slimer overlay labels and frame independence."""
import ast
import unittest
from pathlib import Path
from PIL import Image
from studio.pet_suite_model import PetSuiteModel

SOURCE = Path(__file__).resolve().parents[1] / 'friendly_animator.py'

class SlimerTimelineLabels(unittest.TestCase):
    def test_labels_derive_from_selected_timeline_index(self):
        source = SOURCE.read_text()
        tree = ast.parse(source)
        fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'sync_slimer_asset_labels')
        body = ast.get_source_segment(source, fn)
        self.assertIn("f'Slimer Pose {number:03d}'", body)
        self.assertIn("canonical == 'Slimer pose overlay'", body)
        self.assertIn('index < len(poses[self.frame])', body)
        self.assertNotIn("part['name'] =", body)

    def test_earlier_pose_pixels_unchanged_after_insert_and_overlay_edit(self):
        model = PetSuiteModel()
        red = Image.new('RGBA', (128,128), (255,0,0,255))
        blue = Image.new('RGBA', (128,128), (0,0,255,255))
        model.import_part('Slimer pose overlay', red)
        first = model.insert_frame('Idle / Breathing', 0)
        before = model.render(model.animations['Idle / Breathing'][first]).tobytes()
        model.originals[0] = blue.copy()
        model.parts[0]['image'] = blue.copy()
        model.insert_frame('Idle / Breathing', 1)
        self.assertEqual(before, model.render(model.animations['Idle / Breathing'][0]).tobytes())
        self.assertNotEqual(before, model.render(model.animations['Idle / Breathing'][1]).tobytes())

if __name__ == '__main__': unittest.main()
