import tempfile
import unittest
from pathlib import Path
from PIL import Image
from studio.pet_suite_model import PetSuiteModel

class TestFrameTiming(unittest.TestCase):
    def test_edit_reorder_copy_and_reopen(self):
        m=PetSuiteModel((32,32));m.import_part('Head',Image.new('RGBA',(4,4),'green'))
        m.insert_frame('Walk',0);m.insert_frame('Walk',1)
        m.set_frame_duration('Walk',0,100);m.set_frame_duration('Walk',1,300)
        self.assertEqual([m.playback_frame_at('Walk',t) for t in (0,99,100,399,400)], [0,0,1,1,0])
        m.move_frame('Walk',0,1)
        self.assertEqual(m.frame_durations['Walk'],[300,100])
        m.copy_frame('Walk',1)
        self.assertEqual(m.frame_durations['Walk'],[300,100,100])
        m.delete_frame('Walk',0)
        self.assertEqual(m.frame_durations['Walk'],[100,100])
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'pet.json';m.save_project(path)
            loaded=PetSuiteModel.load_project(path)
            self.assertEqual(loaded.frame_durations['Walk'],[100,100])
    def test_legacy_project_without_timing(self):
        m=PetSuiteModel();m.import_part('Part',Image.new('RGBA',(2,2),'red'))
        m.animations['Idle']=[m.snapshot(),m.snapshot()]
        self.assertEqual(m.frame_duration('Idle',1),125)
        m.set_frame_duration('Idle',1,10)
        self.assertEqual(m.frame_duration('Idle',1),40)

if __name__ == '__main__': unittest.main()
