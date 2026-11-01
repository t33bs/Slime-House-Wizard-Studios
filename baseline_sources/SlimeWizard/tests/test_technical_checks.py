import unittest
from PIL import Image
from studio.pet_suite_model import PetSuiteModel
from studio.technical_checks import check_animation

class TechnicalChecksTest(unittest.TestCase):
    def test_empty_project(self):
        m=PetSuiteModel()
        self.assertEqual(len(check_animation(m,'Idle')),2)
    def test_valid_poses(self):
        m=PetSuiteModel();m.import_part('anything',Image.new('RGBA',(4,4)))
        m.insert_frame('Idle',0)
        self.assertEqual(check_animation(m,'Idle'),[])
    def test_missing_parts_in_pose(self):
        m=PetSuiteModel();m.import_part('one',Image.new('RGBA',(4,4)))
        m.insert_frame('Idle',0);m.import_part('second',Image.new('RGBA',(4,4)))
        self.assertTrue(any('parts' in x.message for x in check_animation(m,'Idle')))
    def test_timing_warning(self):
        m=PetSuiteModel();m.import_part('one',Image.new('RGBA',(4,4)))
        m.insert_frame('Idle',0);m.frame_durations['Idle']=[10]
        self.assertTrue(any('timing' in x.message for x in check_animation(m,'Idle')))
    def test_no_mutation_or_aesthetic_judgment(self):
        m=PetSuiteModel();m.import_part('unusual monster',Image.new('RGBA',(3,9)))
        m.insert_frame('Idle',0);before=m.content_fingerprint() if hasattr(m,'content_fingerprint') else repr(m.animations)
        self.assertEqual(check_animation(m,'Idle'),[])
        after=m.content_fingerprint() if hasattr(m,'content_fingerprint') else repr(m.animations)
        self.assertEqual(before,after)
