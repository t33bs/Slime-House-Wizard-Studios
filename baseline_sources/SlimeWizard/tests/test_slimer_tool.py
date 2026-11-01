import unittest
from PIL import Image
from studio.slimer_tool import SlimerSelection


class SlimerToolTests(unittest.TestCase):
    def setUp(self):
        self.image = Image.new('RGBA', (12, 12), (0, 0, 0, 0))
        self.image.putpixel((2, 3), (10, 220, 40, 255))
        self.tool = SlimerSelection.empty(self.image)

    def test_copy_default_preserves_original(self):
        self.tool.paint(2, 3)
        result = self.tool.compose(self.tool.transform(dx=3))
        self.assertEqual(result.getpixel((2, 3))[3], 255)
        self.assertEqual(result.getpixel((5, 3))[:3], (10, 220, 40))
        self.assertEqual(self.image.getpixel((5, 3))[3], 0)

    def test_move_clears_original(self):
        self.tool.paint(2, 3)
        result = self.tool.compose(self.tool.transform(dx=3), move_original=True)
        self.assertEqual(result.getpixel((2, 3))[3], 0)
        self.assertEqual(result.getpixel((5, 3))[3], 255)

    def test_erase_and_empty_selection(self):
        self.tool.paint(2, 3)
        self.tool.paint(2, 3, erase=True)
        self.assertIsNone(self.tool.mask.getbbox())
        self.assertEqual(self.tool.compose(self.tool.transform()).tobytes(), self.image.tobytes())

    def test_resize_keeps_crisp_pixels(self):
        self.tool.paint(2, 3)
        preview = self.tool.transform(width=3, height=3)
        self.assertEqual(preview.getpixel((4, 5))[3], 255)
        self.assertEqual(preview.getpixel((5, 5))[3], 0)

    def test_reject_mismatched_mask(self):
        with self.assertRaises(ValueError):
            SlimerSelection(self.image, Image.new('L', (3, 3)))


if __name__ == '__main__':
    unittest.main()
