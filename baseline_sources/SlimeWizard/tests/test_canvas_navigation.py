import unittest
from studio.canvas_navigation import geometry,zoom_at
class CanvasNavigationTests(unittest.TestCase):
    def test_center(self):
        scale,x,y=geometry(600,400,128,128)
        self.assertAlmostEqual(x,(600-128*scale)/2)
        self.assertAlmostEqual(y,(400-128*scale)/2)
    def test_pointer_anchor(self):
        before=geometry(600,400,128,128,1,12,-7)
        px,py=233,189
        ix=(px-before[1])/before[0];iy=(py-before[2])/before[0]
        z,x,y=zoom_at(600,400,128,128,1,12,-7,px,py,3)
        after=geometry(600,400,128,128,z,x,y)
        self.assertAlmostEqual(after[1]+ix*after[0],px)
        self.assertAlmostEqual(after[2]+iy*after[0],py)
    def test_limits(self):
        self.assertEqual(zoom_at(600,400,128,128,1,0,0,100,100,100)[0],8)
        self.assertEqual(zoom_at(600,400,128,128,1,0,0,100,100,-100)[0],.25)
    def test_invalid(self):
        with self.assertRaises(ValueError):geometry(0,400,128,128)
        with self.assertRaises(ValueError):geometry(600,400,128,128,0)
