import unittest
from PIL import Image
from studio.timeline_tools import timeline_summary,onion_composite

class TimelineToolsTests(unittest.TestCase):
    def test_summary(self):
        self.assertEqual(timeline_summary([100,200,300])["milliseconds"],600)
    def test_empty(self):
        self.assertEqual(timeline_summary([])["fps_equivalent"],0)
    def test_invalid(self):
        with self.assertRaises(ValueError):timeline_summary([0])
    def test_composite_keeps_current(self):
        cur=Image.new("RGBA",(4,4),(0,0,0,0));cur.putpixel((1,1),(255,0,0,255))
        prev=Image.new("RGBA",(4,4),(0,255,0,255))
        out=onion_composite(cur,prev)
        self.assertEqual(out.getpixel((1,1)),(255,0,0,255))
        self.assertLess(out.getpixel((0,0))[3],255)
        self.assertEqual(prev.getpixel((0,0))[3],255)
    def test_next(self):
        blank=Image.new("RGBA",(2,2));nxt=Image.new("RGBA",(2,2),(0,0,255,255))
        self.assertGreater(onion_composite(blank,following=nxt).getpixel((0,0))[3],0)
    def test_mismatch(self):
        with self.assertRaises(ValueError):onion_composite(Image.new("RGBA",(2,2)),Image.new("RGBA",(3,3)))

if __name__=="__main__":unittest.main()
