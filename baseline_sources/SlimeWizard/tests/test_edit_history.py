import unittest
from PIL import Image
from studio.pet_suite_model import PetSuiteModel
from studio.edit_history import EditHistory

class EditHistoryTests(unittest.TestCase):
    def setUp(self):
        self.model=PetSuiteModel()
        self.model.import_part('paw',Image.new('RGBA',(4,4),(255,0,0,255)))
        self.history=EditHistory()

    def test_undo_redo_geometry(self):
        self.history.record(self.model)
        self.model.move_with_children(0,8,3)
        self.assertTrue(self.history.undo(self.model))
        self.assertEqual(self.model.parts[0]['x'],0)
        self.assertTrue(self.history.redo(self.model))
        self.assertEqual(self.model.parts[0]['x'],8)

    def test_redo_invalidated_by_new_edit(self):
        self.history.record(self.model)
        self.model.move_with_children(0,8,0)
        self.history.undo(self.model)
        self.history.record(self.model)
        self.model.move_with_children(0,2,0)
        self.assertFalse(self.history.redo(self.model))

    def test_restore_layers_pixels_and_rig(self):
        self.history.record(self.model)
        self.model.import_part('ear',Image.new('RGBA',(3,3),(0,255,0,255)))
        self.model.attach(1,0)
        self.model.set_anchor(0,1,1)
        self.model.rotate_part(0,90)
        self.assertTrue(self.history.undo(self.model))
        self.assertEqual(len(self.model.parts),1)
        self.assertEqual(self.model.originals[0].getpixel((0,0)),(255,0,0,255))
        self.assertEqual(self.model.attachments,{})
        self.assertTrue(self.history.redo(self.model))
        self.assertEqual(len(self.model.parts),2)
        self.assertEqual(self.model.angles[0],90)

    def test_animations_and_timing(self):
        self.history.record(self.model)
        self.model.insert_frame('Walk',0)
        self.model.set_frame_duration('Walk',0,260)
        self.history.undo(self.model)
        self.assertNotIn('Walk',self.model.animations)
        self.history.redo(self.model)
        self.assertEqual(self.model.frame_duration('Walk',0),260)

    def test_undo_redo_restores_pose_ids_and_recovery(self):
        self.model.insert_frame('Walk', 0)
        original_id = self.model.pose_id('Walk', 0)
        self.model.pose_recovery[original_id] = ['previous snapshot']
        self.history.record(self.model)
        self.model.copy_frame('Walk', 0)
        copied_id = self.model.pose_id('Walk', 1)
        self.assertNotEqual(original_id, copied_id)
        self.assertTrue(self.history.undo(self.model))
        self.assertEqual(self.model.pose_ids['Walk'], [original_id])
        self.assertEqual(self.model.pose_recovery[original_id], ['previous snapshot'])
        self.assertTrue(self.history.redo(self.model))
        self.assertEqual(self.model.pose_ids['Walk'], [original_id, copied_id])

    def test_deleted_pose_undo_restores_recovery_snapshot(self):
        self.model.insert_frame('Walk', 0)
        pose_id = self.model.pose_id('Walk', 0)
        self.model.pose_recovery[pose_id] = ['recovery copy']
        self.history.record(self.model)
        self.model.delete_frame('Walk', 0)
        self.assertNotIn(pose_id, self.model.pose_recovery)
        self.assertTrue(self.history.undo(self.model))
        self.assertEqual(self.model.pose_id('Walk', 0), pose_id)
        self.assertEqual(self.model.pose_recovery[pose_id], ['recovery copy'])

    def test_bounded_history(self):
        history=EditHistory(limit=2)
        for n in range(4):
            history.record(self.model)
            self.model.move_with_children(0,1,0)
        self.assertEqual(len(history.past),2)

    def test_independent_models(self):
        other=PetSuiteModel();other.import_part('ear',Image.new('RGBA',(2,2)))
        h2=EditHistory();h2.record(other)
        other.move_with_children(0,3,0)
        self.history.record(self.model)
        self.model.move_with_children(0,7,0)
        self.history.undo(self.model)
        self.assertEqual(other.parts[0]['x'],3)
        self.assertTrue(h2.undo(other))
        self.assertEqual(other.parts[0]['x'],0)

if __name__=='__main__':unittest.main()
