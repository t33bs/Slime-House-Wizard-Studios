"""Regression for repeated Slimer placement of translucent sprite pixels."""
import unittest
from PIL import Image

class SlimerAlphaIntegrityTests(unittest.TestCase):
    def test_repeated_placement_preserves_exact_rgba(self):
        old=Image.new('RGBA',(8,8),(0,0,0,0))
        placed=Image.new('RGBA',(8,8),(0,0,0,0))
        placed.putpixel((2,3),(33,99,180,96))
        mask=placed.getchannel('A').point(lambda a:255 if a else 0)
        for _ in range(100):
            old.paste(placed,(0,0),mask)
            self.assertEqual(old.getpixel((2,3)),(33,99,180,96))
            self.assertEqual(old.getpixel((0,0)),(0,0,0,0))

    def test_second_selection_changes_only_selected_pixels(self):
        old=Image.new('RGBA',(8,8),(0,0,0,0))
        old.putpixel((2,3),(33,99,180,96))
        placed=Image.new('RGBA',(8,8),(0,0,0,0))
        placed.putpixel((5,6),(200,30,70,128))
        old.paste(placed,(0,0),placed.getchannel('A').point(lambda a:255 if a else 0))
        self.assertEqual(old.getpixel((2,3)),(33,99,180,96))
        self.assertEqual(old.getpixel((5,6)),(200,30,70,128))

if __name__=='__main__':unittest.main()
