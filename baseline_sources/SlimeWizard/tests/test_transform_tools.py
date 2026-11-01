import unittest
from PIL import Image
from studio.pet_suite_model import PetSuiteModel
from studio.edit_history import EditHistory

class TransformToolTests(unittest.TestCase):
    def setUp(self):
        self.model=PetSuiteModel((20,20))
        img=Image.new('RGBA',(3,2),(0,0,0,0));img.putpixel((0,0),(255,0,0,255))
        self.model.import_part('Ear',img)
        self.history=EditHistory()

    def test_horizontal_flip_pixels_and_dimensions(self):
        self.model.resize_part(0,9,6)
        self.model.flip_part(0,'horizontal')
        self.assertEqual(self.model.parts[0]['image'].size,(9,6))
        self.assertEqual(self.model.originals[0].getpixel((2,0)),(255,0,0,255))

    def test_vertical_flip_pixels(self):
        self.model.flip_part(0,'vertical')
        self.assertEqual(self.model.originals[0].getpixel((0,1)),(255,0,0,255))

    def test_center_each_axis(self):
        self.model.parts[0]['x']=1;self.model.parts[0]['y']=2
        self.model.center_part(0,'horizontal')
        self.assertEqual((self.model.parts[0]['x'],self.model.parts[0]['y']),(8,2))
        self.model.center_part(0,'vertical')
        self.assertEqual((self.model.parts[0]['x'],self.model.parts[0]['y']),(8,9))

    def test_reset_preserves_position(self):
        self.model.resize_part(0,12,12);self.model.parts[0]['x']=5
        self.model.reset_part_size(0)
        self.assertEqual(self.model.parts[0]['image'].size,(3,2))
        self.assertEqual(self.model.parts[0]['x'],5)

    def test_undo_redo_flip_and_center(self):
        self.history.record(self.model)
        self.model.flip_part(0,'horizontal');self.model.center_part(0)
        self.assertTrue(self.history.undo(self.model))
        self.assertEqual(self.model.parts[0]['x'],0)
        self.assertEqual(self.model.originals[0].getpixel((0,0)),(255,0,0,255))
        self.assertTrue(self.history.redo(self.model))
        self.assertEqual(self.model.parts[0]['x'],8)

    def test_invalid_selection_is_safe(self):
        for action in (lambda:self.model.flip_part(2,'horizontal'),lambda:self.model.reset_part_size(2),lambda:self.model.center_part(-1)):
            with self.assertRaises(ValueError):action()

if __name__=='__main__':unittest.main()
