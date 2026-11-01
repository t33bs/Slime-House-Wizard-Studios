"""End-to-end model persistence and export regression tests."""
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


class ProjectExportRoundTripTests(unittest.TestCase):
    def build(self):
        model = PetSuiteModel((24, 20))
        image = Image.new('RGBA', (5, 4), (0, 0, 0, 0))
        image.putpixel((1, 2), (210, 30, 110, 143))
        image.putpixel((3, 1), (0, 0, 0, 255))
        model.import_part('Unusual floating shape', image)
        model.parts[0]['x'] = 2
        model.parts[0]['y'] = 3
        first = model.snapshot()
        second = model.snapshot()
        second[0]['x'] = 12
        third = model.snapshot()
        third[0]['y'] = 11
        model.animations['Float / Spin'] = [first, second, third]
        model.animations['Rest'] = [third, first]
        for name, durations in [('Float / Spin', [110, 270, 490]), ('Rest', [80, 310])]:
            for i, duration in enumerate(durations):
                model.set_frame_duration(name, i, duration)
        return model

    def test_save_reload_and_every_export(self):
        model = self.build()
        fingerprint = model.content_fingerprint()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / 'floating.pet.json'
            model.save_project(project)
            reopened = PetSuiteModel.load_project(project)
            self.assertEqual(reopened.content_fingerprint(), fingerprint)
            sheet = reopened.export(root / 'out', basename='sprite', columns=2, spacing=3)
            meta = json.loads(sheet.with_suffix('.json').read_text())
            self.assertEqual([e['duration_ms'] for e in meta['frames']], [110, 270, 490, 80, 310])
            with Image.open(sheet) as atlas:
                for entry in meta['frames']:
                    rect = entry['rect']
                    crop = atlas.crop((rect['x'], rect['y'], rect['x']+rect['w'], rect['y']+rect['h']))
                    pose = reopened.animations[entry['animation']][entry['frame']]
                    self.assertEqual(crop.tobytes(), reopened.render(pose).tobytes())
            outputs = reopened.export_animations(root / 'out', basename='sprite')
            self.assertEqual(len(outputs), 4)
            for output in outputs:
                with Image.open(output) as animation:
                    self.assertTrue(animation.is_animated)
                    self.assertGreater(animation.n_frames, 1)
                    self.assertEqual(animation.info['loop'], 0)
                    name = 'Float / Spin' if 'Float_Spin' in output.name else 'Rest'
                    expected = [110, 270, 490] if name == 'Float / Spin' else [80, 310]
                    self.assertEqual(animation.n_frames, len(expected))
                    for i, ms in enumerate(expected):
                        animation.seek(i)
                        if output.suffix == '.gif':
                            self.assertLessEqual(abs(animation.info['duration'] - ms), 10)
                        else:
                            self.assertEqual(animation.info['duration'], ms)
                            self.assertEqual(animation.convert('RGBA').tobytes(), reopened.render(reopened.animations[name][i]).tobytes())
            self.assertEqual(reopened.content_fingerprint(), fingerprint)
            self.assertEqual(model.content_fingerprint(), fingerprint)

    def test_reopen_from_different_directory_and_export(self):
        model = self.build()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'nested' / 'pet.json'
            path.parent.mkdir()
            model.save_project(path)
            reopened = PetSuiteModel.load_project(path)
            self.assertEqual(reopened.content_fingerprint(), model.content_fingerprint())
            self.assertEqual(len(reopened.export_animations(Path(tmp) / 'other', gif=False)), 2)


if __name__ == '__main__':
    unittest.main()
