from PIL import Image
from studio.slime_cleaner import erase_visible_pixels


def test_clears_only_target_pixel():
    img=Image.new('RGBA',(4,4),(30,50,70,255))
    parts=[{'image':img,'x':0,'y':0,'visible':True}]
    assert erase_visible_pixels(parts,1,2)
    assert img.getpixel((1,2))[3]==0
    assert img.getpixel((2,2))[3]==255


def test_top_layer_only_and_hidden_preserved():
    base=Image.new('RGBA',(3,3),(255,0,0,255))
    top=Image.new('RGBA',(3,3),(0,255,0,255))
    hidden=Image.new('RGBA',(3,3),(0,0,255,255))
    parts=[{'image':base,'x':0,'y':0,'visible':True},{'image':top,'x':0,'y':0,'visible':True},{'image':hidden,'x':0,'y':0,'visible':False}]
    erase_visible_pixels(parts,1,1)
    assert top.getpixel((1,1))[3]==0
    assert base.getpixel((1,1))[3]==255
    assert hidden.getpixel((1,1))[3]==255


def test_brush_respects_offsets_and_boundaries():
    img=Image.new('RGBA',(2,2),(5,6,7,255))
    parts=[{'image':img,'x':10,'y':20,'visible':True}]
    erase_visible_pixels(parts,10,20,3)
    assert img.getpixel((0,0))[3]==0
    assert img.getpixel((1,1))[3]==0


def test_does_not_clear_again_after_pixel_removed():
    img=Image.new('RGBA',(2,2),(5,6,7,255))
    parts=[{'image':img,'x':0,'y':0,'visible':True}]
    assert erase_visible_pixels(parts,0,0)
    assert not erase_visible_pixels(parts,0,0)
