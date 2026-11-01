"""Round-trip export checks for sprite sheet geometry and timing."""
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from studio.pet_suite_model import PetSuiteModel

class SpriteSheetExportTests(unittest.TestCase):
    def make_model(self):
        model = PetSuiteModel((16, 16))
        model.import_part('pixel', Image.new('RGBA', (2, 2), (200, 20, 40, 255)))
        a = model.snapshot()
        b = model.snapshot()
        b[0]['x'] = 7
        model.animations['Walk'] = [a, b]
        model.set_frame_duration('Walk', 0, 90)
        model.set_frame_duration('Walk', 1, 370)
        return model

    def test_manifest_matches_timeline_and_pixels(self):
        model = self.make_model()
        before = model.content_fingerprint()
        with tempfile.TemporaryDirectory() as tmp:
            png = model.export(tmp, columns=2, spacing=3)
            manifest = json.loads((Path(tmp) / 'creature_sheet.json').read_text())
            self.assertEqual([f['duration_ms'] for f in manifest['frames']], [90, 370])
            self.assertEqual([f['rect']['x'] for f in manifest['frames']], [0, 19])
            with Image.open(png) as atlas:
                self.assertEqual(atlas.size, (35, 16))
                for frame in manifest['frames']:
                    r = frame['rect']
                    crop = atlas.crop((r['x'], r['y'], r['x']+r['w'], r['y']+r['h']))
                    expected = model.render(model.animations[frame['animation']][frame['frame']])
                    self.assertEqual(crop.tobytes(), expected.tobytes())
        self.assertEqual(before, model.content_fingerprint())

    def test_multiple_animations_preserve_order(self):
        model = self.make_model()
        model.animations['Blink'] = [model.snapshot()]
        model.set_frame_duration('Blink', 0, 610)
        with tempfile.TemporaryDirectory() as tmp:
            model.export(tmp, columns=2)
            frames = json.loads((Path(tmp) / 'creature_sheet.json').read_text())['frames']
            self.assertEqual([(f['animation'], f['frame'], f['duration_ms']) for f in frames],
                             [('Walk', 0, 90), ('Walk', 1, 370), ('Blink', 0, 610)])

    def test_empty_timeline_still_exports_current_sprite(self):
        model = PetSuiteModel((8, 8))
        with tempfile.TemporaryDirectory() as tmp:
            path = model.export(tmp)
            self.assertTrue(path.exists())
            frames = json.loads((Path(tmp) / 'creature_sheet.json').read_text())['frames']
            self.assertEqual(len(frames), 1)

if __name__ == '__main__':
    unittest.main()
