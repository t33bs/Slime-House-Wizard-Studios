import tempfile
import unittest
from pathlib import Path
from PIL import Image
from studio.apng_export import encode_apng
from studio.pet_suite_model import PetSuiteModel

class APNGFidelityTests(unittest.TestCase):
    def frames(self):
        first = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        first.putpixel((2, 3), (15, 125, 240, 117))
        first.putpixel((4, 3), (0, 0, 0, 255))
        second = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        second.putpixel((9, 8), (240, 18, 7, 199))
        return [first, second]

    def test_lossless_rgba_motion_timing_and_loop(self):
        frames = self.frames()
        original = [f.tobytes() for f in frames]
        with tempfile.TemporaryDirectory() as temp:
            path = encode_apng(frames, [110, 275], Path(temp) / "walk.png")
            with Image.open(path) as animation:
                self.assertTrue(animation.is_animated)
                self.assertEqual(animation.n_frames, 2)
                self.assertEqual(animation.info["loop"], 0)
                for i, duration in enumerate((110, 275)):
                    animation.seek(i)
                    self.assertEqual(animation.info["duration"], duration)
                    self.assertEqual(animation.convert("RGBA").tobytes(), original[i])
        self.assertEqual([f.tobytes() for f in frames], original)

    def test_invalid_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "no.png"
            for frames, durations in (([], []), (self.frames(), [100]),
                                      (self.frames(), [0, 100]),
                                      ([self.frames()[0], Image.new("RGBA", (4, 4))], [100, 100])):
                with self.subTest(durations=durations):
                    with self.assertRaises(ValueError):
                        encode_apng(frames, durations, output)
            self.assertFalse(output.exists())

    def test_model_export_integration(self):
        model = PetSuiteModel((16, 16))
        model.import_part("sprite", Image.new("RGBA", (2, 2), (20, 120, 220, 160)))
        a = model.snapshot()
        b = model.snapshot()
        b[0]["x"] = 6
        model.animations["Walking"] = [a, b]
        model.set_frame_duration("Walking", 0, 110)
        model.set_frame_duration("Walking", 1, 275)
        before = model.content_fingerprint()
        with tempfile.TemporaryDirectory() as temp:
            outputs = model.export_animations(temp, gif=False, apng=True)
            self.assertEqual(len(outputs), 1)
            with Image.open(outputs[0]) as img:
                self.assertEqual(img.n_frames, 2)
                for i, pose in enumerate((a, b)):
                    img.seek(i)
                    self.assertEqual(img.convert("RGBA").tobytes(), model.render(pose).convert("RGBA").tobytes())
        self.assertEqual(before, model.content_fingerprint())
