import unittest
from studio.window_geometry import fit_window_rect

class WindowGeometryTests(unittest.TestCase):
    def test_1080p(self):
        self.assertEqual(fit_window_rect((50,50,1380,850),[(0,0,1920,1040)]),(50,50,1380,850))
    def test_small_screen(self):
        self.assertEqual(fit_window_rect((0,0,1380,850),[(0,0,800,600)]),(0,0,800,600))
    def test_offscreen_restore(self):
        self.assertEqual(fit_window_rect((2000,500,900,700),[(0,0,1280,720)]),(380,20,900,700))
    def test_negative_monitor(self):
        self.assertEqual(fit_window_rect((-1500,100,1000,700),[(-1920,0,1920,1040),(0,0,1920,1040)]),(-1500,100,1000,700))
    def test_multiple_displays(self):
        self.assertEqual(fit_window_rect((1800,100,1100,800),[(0,0,1920,1040),(1920,0,1280,1024)]),(1920,100,1100,800))
    def test_tiny_screen(self):
        self.assertEqual(fit_window_rect((0,0,900,700),[(0,0,400,300)]),(0,0,400,300))
    def test_no_screen(self):
        self.assertEqual(fit_window_rect((1,2,3,4),[]),(1,2,3,4))
