"""Phase 15 timeline insertion preserves independent pose snapshots."""
import unittest
from PIL import Image
from studio.pet_suite_model import PetSuiteModel

class TimelineInsertionTests(unittest.TestCase):
    def test_inserting_in_middle_preserves_both_neighbor_poses(self):
        model = PetSuiteModel()
        source = Image.new('RGBA', (128, 128))
        source.putpixel((2, 2), (255, 0, 0, 255))
        model.import_part('source', source)
        model.insert_frame('Idle / Breathing', 0)
        model.parts[0]['x'] = 10
        model.insert_frame('Idle / Breathing', 1)
        before = [pose[0]['x'] for pose in model.animations['Idle / Breathing']]
        model.parts[0]['x'] = 5
        inserted = model.insert_frame('Idle / Breathing', 1)
        self.assertEqual(inserted, 1)
        self.assertEqual([pose[0]['x'] for pose in model.animations['Idle / Breathing']], [before[0], 5, before[1]])
        model.parts[0]['x'] = 99
        self.assertEqual([pose[0]['x'] for pose in model.animations['Idle / Breathing']], [before[0], 5, before[1]])
