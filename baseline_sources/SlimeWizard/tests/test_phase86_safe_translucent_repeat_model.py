"""Phase 86: isolate fractional-alpha source ownership before Move Original.

A safely isolated semitransparent source pixel may move; blending two
contributing layers or partially choosing an enlarged source pixel may not.
"""
import ast
from pathlib import Path

from PIL import Image, ImageChops
from studio.pet_suite_model import PetSuiteModel


def methods():
    tree = ast.parse((Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text())
    names = ('_slimer_layered_erase_plan', '_slimer_transformed_erase_plan',
             '_slimer_original_erase_safe', '_slimer_erase_original_layers',
             '_slimer_selection_safety_details')
    functions = {node.name: node for node in ast.walk(tree)
                 if isinstance(node, ast.FunctionDef) and node.name in names}
    ns = {'Image': Image, 'ImageChops': ImageChops}
    exec(compile(ast.Module(body=[functions[n] for n in names], type_ignores=[]),
                 '<live production methods>', 'exec'), ns)
    return type('Editor', (), {name: ns[name] for name in names})

Editor = methods()


def pick(size, *points):
    mask = Image.new('L', size)
    for pt in points:
        mask.putpixel(pt, 255)
    return mask


def test_single_layer_translucent_source_can_move_without_changing_alpha():
    model = PetSuiteModel((32,32))
    source = Image.new('RGBA', model.size)
    source.putpixel((3,3), (250,40,60,113))
    source.putpixel((4,3), (60,30,140,255))
    model.import_part('original', source)
    edit = Editor(); edit.model = model; edit._slimer_pending_part = None
    mask = pick(model.size, (3,3))
    assert edit._slimer_original_erase_safe(mask)
    plan = edit._slimer_layered_erase_plan(mask)
    assert plan == [(0, {3 + 3*32})]
    # Before erasing, staging exactly preserves the rendered RGBA.
    source_render = model.render()
    staged = Image.new('RGBA', model.size)
    staged.putpixel((3,3), source_render.getpixel((3,3)))
    model.import_part('Slimer Layer 001', staged)
    edit._slimer_pending_part = model.parts[-1]
    model.parts[-1]['x'] = 8
    edit._slimer_erase_original_layers(mask)
    assert model.render().getpixel((3,3))[3] == 0
    assert model.render().getpixel((11,3)) == (250,40,60,113)
    assert model.render().getpixel((4,3)) == (60,30,140,255)


def test_translucent_pixel_over_another_visible_layer_must_still_be_rejected():
    model = PetSuiteModel((32,32))
    lower = Image.new('RGBA', model.size)
    upper = Image.new('RGBA', model.size)
    lower.putpixel((5,5), (100,120,250,255))
    upper.putpixel((5,5), (250,20,20,128))
    model.import_part('lower', lower)
    model.import_part('upper', upper)
    edit = Editor(); edit.model=model
    mask = pick(model.size, (5,5))
    assert edit._slimer_layered_erase_plan(mask) is None
    assert not edit._slimer_original_erase_safe(mask)
    before = model.render().tobytes()
    assert model.render().tobytes() == before
    details = edit._slimer_selection_safety_details(mask, model.render())
    assert 'selected=1' in details and 'multi-layer=1' in details


def test_multilayer_unrelated_translucency_does_not_block_new_source_region():
    model = PetSuiteModel((32,32))
    original = Image.new('RGBA', model.size)
    moved = Image.new('RGBA', model.size)
    original.putpixel((5,5), (180,55,120,128))
    original.putpixel((6,5), (140,190,60,255))
    moved.putpixel((17,17), (55,145,230,165))
    model.import_part('original', original)
    model.import_part('previously moved Slimer layer', moved)
    model.rotate_part(1, 5)
    edit = Editor(); edit.model = model
    for location in ((5,5),(6,5)):
        mask=pick(model.size, location)
        assert edit._slimer_layered_erase_plan(mask) is not None
        assert edit._slimer_original_erase_safe(mask)


def test_partially_selected_enlarged_fractional_source_is_not_erased():
    model = PetSuiteModel((32,32))
    img=Image.new('RGBA',(2,1))
    img.putpixel((0,0),(100,30,255,128))
    model.import_part('scaled source',img)
    model.resize_part(0,4,2)
    model.parts[0]['x']=5
    model.parts[0]['y']=5
    edit=Editor();edit.model=model
    assert edit._slimer_layered_erase_plan(pick(model.size, (5,5))) is None
    assert not edit._slimer_original_erase_safe(pick(model.size, (5,5)))
    full=pick(model.size,*[(x,y) for x in (5,6) for y in (5,6)])
    assert edit._slimer_layered_erase_plan(full) is not None


def test_two_consecutive_pixel_moves_after_one_layer_has_been_resized():
    model = PetSuiteModel((32,32))
    source = Image.new('RGBA',model.size)
    source.putpixel((3,3),(210,20,90,255))
    source.putpixel((12,12),(210,20,90,156))
    model.import_part('source',source)
    edit=Editor();edit.model=model
    # First move using Move Original, leave a transformed transparent layer behind.
    first=pick(model.size,(3,3))
    staged=Image.new('RGBA',model.size)
    staged.putpixel((3,3),source.getpixel((3,3)))
    model.import_part('Slimer Layer 001',staged)
    edit._slimer_pending_part=model.parts[-1]
    model.parts[-1]['x']=4
    edit._slimer_erase_original_layers(first)
    edit._slimer_pending_part=None
    # Edit the staged part's dimensions/anchor as a previous Slimer operation.
    model.set_anchor(1,3,3)
    model.rotate_part(1,15)
    # The second source is independent, semitransparent, and *must* stage.
    second=pick(model.size,(12,12))
    assert edit._slimer_original_erase_safe(second)
    overlay=Image.new('RGBA',model.size)
    overlay.putpixel((12,12),model.render().getpixel((12,12)))
    model.import_part('Slimer Layer 002', overlay)
    edit._slimer_pending_part=model.parts[-1]
    model.parts[-1]['x']=6
    edit._slimer_erase_original_layers(second)
    assert model.render().getpixel((12,12))[3] == 0
    assert model.render().getpixel((18,12)) == (210,20,90,156)
