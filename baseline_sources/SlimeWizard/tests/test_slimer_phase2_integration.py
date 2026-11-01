import unittest
from PIL import Image
from studio.slimer_tool import SlimerSelection
from studio.pet_suite_model import PetSuiteModel
from studio.edit_history import EditHistory

class SlimerPlacementHistoryTests(unittest.TestCase):
    def test_layer_and_frame_undo_redo_as_one_action(self):
        model=PetSuiteModel((16,16))
        model.import_part('base',Image.new('RGBA',(16,16),(30,50,60,255)))
        model.save_frame('Idle')
        selection=SlimerSelection.empty(model.render())
        selection.paint(3,3)
        history=EditHistory()
        history.record(model)
        layer=selection.transform(dx=2)
        model.import_part('Slimer pose',layer)
        model.insert_frame('Idle',1)
        self.assertEqual(len(model.parts),2)
        self.assertEqual(len(model.animations['Idle']),2)
        self.assertTrue(history.undo(model))
        self.assertEqual(len(model.parts),1)
        self.assertEqual(len(model.animations['Idle']),1)
        self.assertTrue(history.redo(model))
        self.assertEqual(len(model.parts),2)
        self.assertEqual(len(model.animations['Idle']),2)
        self.assertEqual(model.parts[1]['image'].getpixel((5,3)),(30,50,60,255))

if __name__=='__main__':unittest.main()
