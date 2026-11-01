"""Phase98 headless gates: no source-only erasing or timer-triggered pose overwrite."""
from PIL import Image
from studio.pet_suite_model import PetSuiteModel
from studio.slime_cleaner import erase_visible_pixels


def test_cleaner_erases_latest_visible_layer_not_imported_original():
    model = PetSuiteModel()
    base = Image.new('RGBA', (128, 128))
    base.putpixel((20, 20), (220, 80, 10, 255))
    model.import_part('Original Source', base)
    original = model.snapshot()
    model.insert_frame('Idle / Breathing', 0, original)
    overlay = Image.new('RGBA', (128, 128))
    overlay.putpixel((20, 20), (10, 200, 80, 255))
    model.import_part('Combined Artwork 002', overlay)
    model.parts[0]['visible'] = False
    model.insert_frame('Idle / Breathing', 1, model.snapshot())
    before1 = model.render(model.animations['Idle / Breathing'][0]).tobytes()
    before2 = model.render(model.animations['Idle / Breathing'][1]).tobytes()
    changed = set()
    assert erase_visible_pixels(model.parts, 20, 20, states=model.resolved_pose(),
                                canvas_size=model.size, modified_indices=changed)
    assert changed == {1}
    for idx in changed:
        model.originals[idx] = model.parts[idx]['image'].copy()
    assert model.render().getpixel((20, 20))[3] == 0
    assert model.originals[0].getpixel((20, 20)) == (220, 80, 10, 255)
    # The original saved frame and the pre-erase second saved frame are unchanged.
    assert model.render(model.animations['Idle / Breathing'][0]).tobytes() == before1
    assert model.render(model.animations['Idle / Breathing'][1]).tobytes() == before2


def test_cleaner_respects_rotated_editable_layer_and_lower_layer():
    model = PetSuiteModel()
    model.import_part('Original', Image.new('RGBA', (128, 128), (55, 66, 77, 255)))
    top = Image.new('RGBA', (128, 128))
    top.putpixel((20, 40), (10, 255, 60, 230))
    top.putpixel((50, 50), (80, 90, 100, 255))
    model.import_part('Transformed Slimer Layer', top)
    model.angles[1] = 90
    states = model.resolved_pose()
    for i, state in enumerate(states):
        image = model.parts[i]['image']
        state['_cleaner_anchor'] = (image.width // 2, image.height // 2)
    image = model.render_part(1, states[1])
    bbox = image.getchannel('A').getbbox()
    assert bbox is not None
    cx, cy = next((xx, yy) for yy in range(bbox[1], bbox[3])
                  for xx in range(bbox[0], bbox[2])
                  if image.getpixel((xx, yy))[3] > 0)
    before_lower = model.originals[0].tobytes()
    modified = set()
    assert erase_visible_pixels(model.parts, cx, cy, states=states,
                                canvas_size=model.size, modified_indices=modified)
    assert modified == {1}
    model.originals[1] = model.parts[1]['image'].copy()
    assert model.render_part(1, model.resolved_pose()[1]).getpixel((cx, cy))[3] == 0
    assert model.originals[0].tobytes() == before_lower
    # Underlying pixel is now revealed; only the top layer was actually erased.
    assert model.render().getpixel((cx, cy)) == (55, 66, 77, 255)
