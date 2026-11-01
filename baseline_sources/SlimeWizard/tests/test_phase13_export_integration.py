"""Phase 13 integration coverage: saved poses -> reload -> all export formats."""
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from studio.pet_suite_model import PetSuiteModel


class Phase13ExportIntegration(unittest.TestCase):
    def test_independent_poses_survive_reload_and_exports_without_mutation(self):
        model = PetSuiteModel((16, 16))
        pixels = Image.new('RGBA', (3, 3), (0, 0, 0, 0))
        pixels.putpixel((1, 1), (33, 177, 221, 137))
        model.import_part('transparent sample', pixels)
        pose_a = model.snapshot()
        pose_b = model.snapshot()
        pose_b[0]['x'] = 8
        pose_c = model.snapshot()
        pose_c[0]['y'] = 9
        model.animations['Walk'] = [pose_a, pose_b]
        model.animations['Idle'] = [pose_c, pose_a]
        for name, values in [('Walk', [120, 240]), ('Idle', [160, 320])]:
            for i, value in enumerate(values):
                model.set_frame_duration(name, i, value)
        fingerprint = model.content_fingerprint()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = root / 'cat.pet.json'
            model.save_project(project)
            loaded = PetSuiteModel.load_project(project)
            self.assertEqual(loaded.content_fingerprint(), fingerprint)
            self.assertNotEqual(loaded.render(pose_a).tobytes(), loaded.render(pose_b).tobytes())
            self.assertNotEqual(loaded.render(pose_a).tobytes(), loaded.render(pose_c).tobytes())
            sheet = loaded.export(root / 'exports', basename='test', columns=2, spacing=1)
            entries = json.loads(sheet.with_suffix('.json').read_text())['frames']
            self.assertEqual([(e['animation'], e['duration_ms']) for e in entries],
                             [('Walk', 120), ('Walk', 240), ('Idle', 160), ('Idle', 320)])
            with Image.open(sheet) as atlas:
                for entry in entries:
                    rect = entry['rect']
                    frame = atlas.crop((rect['x'], rect['y'], rect['x'] + rect['w'], rect['y'] + rect['h']))
                    expected = loaded.render(loaded.animations[entry['animation']][entry['frame']])
                    self.assertEqual(frame.tobytes(), expected.tobytes())
            outputs = loaded.export_animations(root / 'exports', basename='test')
            self.assertEqual({p.suffix for p in outputs}, {'.gif', '.png'})
            self.assertEqual(len(outputs), 4)
            for output in outputs:
                with Image.open(output) as image:
                    self.assertEqual(image.n_frames, 2)
                    self.assertEqual(image.info.get('loop'), 0)
                    if output.suffix == '.png':
                        name = 'Walk' if 'Walk' in output.name else 'Idle'
                        for index, expected_duration in enumerate(([120, 240] if name == 'Walk' else [160, 320])):
                            image.seek(index)
                            self.assertEqual(image.info['duration'], expected_duration)
                            self.assertEqual(image.convert('RGBA').tobytes(),
                                             loaded.render(loaded.animations[name][index]).tobytes())
            self.assertEqual(loaded.content_fingerprint(), fingerprint)
            self.assertEqual(model.content_fingerprint(), fingerprint)


if __name__ == '__main__':
    unittest.main()
