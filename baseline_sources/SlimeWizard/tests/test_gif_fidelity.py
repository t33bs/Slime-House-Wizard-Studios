import tempfile
import unittest
from pathlib import Path
from PIL import Image
from studio.gif_export import encode_gif


class GifFidelityTests(unittest.TestCase):
    def test_moving_transparent_frames_timing_and_loop(self):
        frames=[]
        for x in (1, 7, 12):
            im=Image.new('RGBA',(20,20),(0,0,0,0))
            for yy in range(2,6):
                for xx in range(x,x+4): im.putpixel((xx,yy),(255,0,0,255))
            frames.append(im)
        originals=[f.tobytes() for f in frames]
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'moving.gif'
            encode_gif(frames,[100,250,135],out)
            with Image.open(out) as gif:
                self.assertEqual(gif.n_frames,3)
                self.assertEqual(gif.info['loop'],0)
                for i,x in enumerate((1,7,12)):
                    gif.seek(i)
                    self.assertEqual(gif.info['duration'],[100,250,140][i])
                    rgba=gif.convert('RGBA')
                    self.assertEqual(rgba.getpixel((x,3))[:3],(255,0,0))
                    self.assertEqual(rgba.getpixel((0,0))[3],0)
                    self.assertEqual(rgba.getpixel((19,19))[3],0)
        self.assertEqual(originals,[f.tobytes() for f in frames])

    def test_rejects_invalid_inputs(self):
        f=Image.new('RGBA',(4,4))
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'x.gif'
            for frames, durations in (([],[]),([f],[0]),([f],[100,200]),([f,Image.new('RGBA',(2,2))],[100,100])):
                with self.assertRaises(ValueError): encode_gif(frames,durations,out)

    def test_transparency_does_not_turn_black_opaque(self):
        a=Image.new('RGBA',(8,8),(0,0,0,0))
        a.putpixel((3,3),(0,0,0,255))
        b=a.copy();b.putpixel((3,3),(0,0,0,0));b.putpixel((4,4),(0,0,0,255))
        with tempfile.TemporaryDirectory() as d:
            encode_gif([a,b],[100,100],Path(d)/'black.gif')
            with Image.open(Path(d)/'black.gif') as gif:
                self.assertEqual(gif.convert('RGBA').getpixel((3,3)),(0,0,0,255))
                gif.seek(1)
                self.assertEqual(gif.convert('RGBA').getpixel((4,4)),(0,0,0,255))
