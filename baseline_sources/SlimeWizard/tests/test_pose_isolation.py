import unittest
from copy import deepcopy
from PIL import Image
from studio.pet_suite_model import PetSuiteModel
from studio.edit_history import EditHistory

class PoseIsolationTests(unittest.TestCase):
    def setUp(self):
        self.model=PetSuiteModel()
        self.model.import_part('unusual creature part',Image.new('RGBA',(12,8),'red'))
        self.model.insert_frame('Walking',0)
        self.model.insert_frame('Walking',1)
        self.model.insert_frame('Idle',0)
    def test_edit_only_one_pose(self):
        before=deepcopy(self.model.animations)
        self.model.edit_pose_at('Walking',1,{0:{'x':29,'angle':83}})
        self.assertEqual(self.model.animations['Walking'][1][0]['x'],29)
        self.assertEqual(self.model.animations['Walking'][0],before['Walking'][0])
        self.assertEqual(self.model.animations['Idle'],before['Idle'])
    def test_save_selected_pose_only(self):
        before=deepcopy(self.model.animations)
        self.model.parts[0]['x']=73
        self.model.save_pose_at('Walking',0)
        self.assertEqual(self.model.animations['Walking'][0][0]['x'],73)
        self.assertEqual(self.model.animations['Walking'][1],before['Walking'][1])
        self.assertEqual(self.model.animations['Idle'],before['Idle'])
    def test_independent_pose_copies(self):
        self.model.edit_pose_at('Walking',0,{0:{'width':19,'height':5}})
        self.assertEqual(self.model.animations['Walking'][1][0]['width'],12)
    def test_invalid_edit_is_atomic(self):
        before=deepcopy(self.model.animations)
        with self.assertRaises(ValueError):
            self.model.edit_pose_at('Walking',0,{0:{'x':5,'width':0}})
        self.assertEqual(self.model.animations,before)
    def test_undo_and_redo_pose(self):
        history=EditHistory();history.record(self.model)
        self.model.edit_pose_at('Walking',0,{0:{'x':44}})
        self.assertTrue(history.undo(self.model))
        self.assertNotEqual(self.model.animations['Walking'][0][0]['x'],44)
        self.assertTrue(history.redo(self.model))
        self.assertEqual(self.model.animations['Walking'][0][0]['x'],44)

if __name__=='__main__':unittest.main()
