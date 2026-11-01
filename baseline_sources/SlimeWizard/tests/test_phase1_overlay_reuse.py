"""Regression coverage for repeated Slimer pose placement and frame isolation."""
import ast
import unittest
from pathlib import Path
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


class SlimerOverlayReuseTests(unittest.TestCase):
    def test_place_frame_uses_existing_overlay(self):
        source=Path(__file__).resolve().parents[1].joinpath('friendly_animator.py').read_text()
        tree=ast.parse(source)
        method=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='_slimer_commit')
        body=ast.get_source_segment(source,method)
        self.assertIn("'Slimer pose overlay'",body)
        self.assertIn('merged.paste(placed',body)
        self.assertNotIn("import_part('Slimer pose'",body)

    def test_hidden_overlay_is_not_reused_as_visible_artwork(self):
        source=Path(__file__).resolve().parents[1].joinpath('friendly_animator.py').read_text()
        tree=ast.parse(source)
        method=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='_slimer_commit')
        body=ast.get_source_segment(source,method)
        self.assertIn("self.model.parts[overlay_index].get('visible', True)",body)
        self.assertIn("old_layer=Image.new('RGBA', self.model.size)",body)

    def test_binary_mask_preserves_exact_translucent_rgba(self):
        # A fractional alpha used as the paste mask would square the alpha
        # rather than preserve the selected pixel's exact RGBA value.
        existing=Image.new('RGBA',(3,3),(0,0,0,0))
        selected=Image.new('RGBA',(3,3),(0,0,0,0))
        selected.putpixel((1,1),(35,105,220,96))
        mask=selected.getchannel('A').point(lambda a: 255 if a else 0)
        for _ in range(10):
            existing.paste(selected,(0,0),mask)
            self.assertEqual(existing.getpixel((1,1)),(35,105,220,96))
            self.assertEqual(existing.getpixel((0,0)),(0,0,0,0))

    def test_reusing_layer_keeps_earlier_frames_immutable(self):
        m=PetSuiteModel((16,16))
        base=Image.new('RGBA',(16,16),(0,0,0,0))
        base.putpixel((3,3),(255,0,0,255))
        m.import_part('Base',base)
        overlay=Image.new('RGBA',(16,16),(0,0,0,0))
        m.import_part('Slimer pose overlay',overlay)
        first=m.insert_frame('Idle',0)
        first_pixels=m.render(m.animations['Idle'][first]).tobytes()
        for step in range(1,11):
            updated=m.originals[1].copy()
            updated.putpixel((step,5),(0,255,0,255))
            m.originals[1]=updated.copy()
            m.parts[1]['image']=updated.copy()
            m.insert_frame('Idle',step)
            self.assertEqual(m.render(m.animations['Idle'][0]).tobytes(),first_pixels)
            self.assertEqual(len(m.parts),2)
        self.assertEqual(len(m.animations['Idle']),11)
        self.assertNotEqual(m.render(m.animations['Idle'][0]).tobytes(),m.render(m.animations['Idle'][-1]).tobytes())

if __name__=='__main__':unittest.main()
