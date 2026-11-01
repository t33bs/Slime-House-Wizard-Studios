"""Release-gate regression tests for exact timeline artwork after save/export."""
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


class ReleasePixelIntegrityTests(unittest.TestCase):
    def test_pose_pixels_survive_save_reopen_and_atlas_export(self):
        m = PetSuiteModel((24, 24))
        part = Image.new('RGBA', (4, 4), (30, 140, 220, 128))
        part.putpixel((0, 0), (240, 20, 90, 255))
        m.import_part('foot', part)
        for x in (1, 6, 11):
            m.parts[0]['x'] = x
            m.insert_frame('Walk', len(m.animations.get('Walk', [])))
        expected = [m.render(p).tobytes() for p in m.animations['Walk']]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'creature.json'
            m.save_project(path)
            loaded = PetSuiteModel.load_project(path)
            self.assertEqual([loaded.render(p).tobytes() for p in loaded.animations['Walk']], expected)
            atlas_path = loaded.export(tmp, basename='release_check', columns=3)
            frames = json.loads((Path(tmp) / 'release_check_sheet.json').read_text())['frames']
            with Image.open(atlas_path) as atlas:
                for frame, pixels in zip(frames, expected):
                    r = frame['rect']
                    self.assertEqual(atlas.crop((r['x'], r['y'], r['x'] + r['w'], r['y'] + r['h'])).tobytes(), pixels)

    def test_new_creature_has_no_previous_creature_pixels(self):
        previous = PetSuiteModel((16, 16))
        previous.import_part('old swordcat', Image.new('RGBA', (16, 16), (10, 20, 30, 255)))
        previous.insert_frame('Idle', 0)
        fresh = PetSuiteModel((16, 16))
        self.assertEqual(fresh.render().getbbox(), None)
        self.assertEqual(fresh.animations, {})
        self.assertNotEqual(previous.render().tobytes(), fresh.render().tobytes())
