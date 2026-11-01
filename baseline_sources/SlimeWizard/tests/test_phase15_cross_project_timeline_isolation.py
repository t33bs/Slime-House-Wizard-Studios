"""Recipe-free project switching: independent poses, timing, playback and export."""
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from studio.animation_registry import available_animation_names, preferred_animation
from studio.pet_suite_model import PetSuiteModel


class CrossProjectTimelineIsolationTests(unittest.TestCase):
    def make_project(self, name, durations, color):
        model = PetSuiteModel((24, 24))
        img = Image.new('RGBA', (3, 3), color)
        model.import_part('shape', img)
        poses = []
        for x in (1, 7, 13):
            model.parts[0]['x'] = x
            poses.append(model.snapshot())
        model.animations[name] = poses
        model.current = name
        for i, duration in enumerate(durations):
            model.set_frame_duration(name, i, duration)
        return model

    def test_alternating_project_load_preserves_pose_pixels_and_timing(self):
        a = self.make_project('Pooping', [90, 180, 360], (255, 0, 0, 255))
        b = self.make_project('My Creature Dance', [120, 240, 480], (0, 0, 255, 255))
        with tempfile.TemporaryDirectory() as tmp:
            a_path, b_path = Path(tmp)/'a.json', Path(tmp)/'b.json'
            a.save_project(a_path)
            b.save_project(b_path)
            expected = [(a, 'Pooping', [90, 180, 360]), (b, 'My Creature Dance', [120, 240, 480])]
            for _ in range(3):
                for original, name, times in expected:
                    path = a_path if name == 'Pooping' else b_path
                    reopened = PetSuiteModel.load_project(path)
                    self.assertEqual(reopened.content_fingerprint(), original.content_fingerprint())
                    self.assertEqual(preferred_animation(reopened), name)
                    self.assertIn(name, available_animation_names(reopened))
                    self.assertEqual([reopened.frame_duration(name, i) for i in range(3)], times)
                    self.assertEqual([reopened.playback_frame_at(name, sum(times[:i])) for i in range(3)], [0, 1, 2])
                    for i in range(3):
                        self.assertEqual(reopened.render(reopened.animations[name][i]).tobytes(), original.render(original.animations[name][i]).tobytes())
            self.assertNotIn('My Creature Dance', available_animation_names(PetSuiteModel.load_project(a_path)))

    def test_exporting_one_project_does_not_change_other_project(self):
        a = self.make_project('Walking', [80, 160, 320], (50, 200, 50, 255))
        b = self.make_project('Custom Twirl', [110, 220, 440], (200, 50, 200, 255))
        before_a, before_b = a.content_fingerprint(), b.content_fingerprint()
        with tempfile.TemporaryDirectory() as tmp:
            for model, name, times in [(a, 'Walking', [80, 160, 320]), (b, 'Custom Twirl', [110, 220, 440])]:
                sheet = model.export(Path(tmp)/name.replace(' ', '_'), basename='sheet')
                metadata = json.loads(sheet.with_suffix('.json').read_text())
                entries = [entry for entry in metadata['frames'] if entry['animation'] == name]
                self.assertEqual([entry['duration_ms'] for entry in entries], times)
                with Image.open(sheet) as atlas:
                    for entry in entries:
                        rect = entry['rect']
                        actual = atlas.crop((rect['x'], rect['y'], rect['x'] + rect['w'], rect['y'] + rect['h']))
                        expected = model.render(model.animations[name][entry['frame']])
                        self.assertEqual(actual.tobytes(), expected.tobytes())
            self.assertEqual(a.content_fingerprint(), before_a)
            self.assertEqual(b.content_fingerprint(), before_b)


if __name__ == '__main__':
    unittest.main()
