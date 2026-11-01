import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


class AtomicAssetTests(unittest.TestCase):
    def test_failed_manifest_commit_keeps_old_pixels_and_removes_staging(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'pet.json'
            model = PetSuiteModel()
            model.import_part('cat', Image.new('RGBA', (3, 3), (255, 0, 0, 255)))
            model.save_project(path)
            old_manifest = path.read_bytes()
            old_assets = json.loads(old_manifest)['asset_dir']
            model.originals[0] = Image.new('RGBA', (3, 3), (0, 0, 255, 255))
            with patch('studio.pet_suite_model.os.replace', side_effect=OSError('failed commit')):
                with self.assertRaises(OSError):
                    model.save_project(path)
            self.assertEqual(path.read_bytes(), old_manifest)
            self.assertEqual(PetSuiteModel.load_project(path).originals[0].getpixel((0, 0)), (255, 0, 0, 255))
            self.assertEqual([p.name for p in Path(d).glob('pet_assets_*')], [old_assets])

    def test_successive_saves_reference_distinct_assets(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'pet.json'
            model = PetSuiteModel()
            model.import_part('cat', Image.new('RGBA', (2, 2), 'red'))
            model.save_project(path)
            first = json.loads(path.read_text())['asset_dir']
            model.originals[0] = Image.new('RGBA', (2, 2), 'blue')
            model.save_project(path)
            second = json.loads(path.read_text())['asset_dir']
            self.assertNotEqual(first, second)
            self.assertTrue((Path(d) / first / 'original_000.png').exists())
            self.assertEqual(PetSuiteModel.load_project(path).originals[0].getpixel((0, 0)), (0, 0, 255, 255))
