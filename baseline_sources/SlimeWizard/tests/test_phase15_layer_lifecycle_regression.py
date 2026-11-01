"""Layer identity and pose-persistence regression checks for the new Slimer workflow."""
from pathlib import Path
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


def test_two_independent_layer_assets_and_pose_restore(tmp_path):
    model = PetSuiteModel((16, 16))
    source = Image.new('RGBA', (16, 16))
    source.putpixel((2, 2), (255, 0, 0, 255))
    source.putpixel((7, 7), (0, 0, 255, 255))
    model.import_part('source', source)
    for number, xy, offset in ((1, (2, 2), (3, 2)), (2, (7, 7), (9, 7))):
        isolated = Image.new('RGBA', (16, 16))
        isolated.putpixel(xy, model.render().getpixel(xy))
        model.import_part(f'Slimer Layer {number:03d}', isolated)
        model.parts[-1]['x'] = offset[0] - xy[0]
        model.parts[-1]['y'] = offset[1] - xy[1]
        # Simulate a successful Move Original commit without altering the
        # source of any already confirmed Slimer layer.
        old = model.originals[0].copy()
        old.putpixel(xy, (0, 0, 0, 0))
        model.originals[0] = old
        model.resize_part(0, 16, 16)
    assert model.render().getpixel((3, 2)) == (255, 0, 0, 255)
    assert model.render().getpixel((9, 7)) == (0, 0, 255, 255)
    model.save_frame('idle')
    first = model.snapshot()
    model.parts[1]['x'] += 2
    model.save_frame('idle')
    second = model.snapshot()
    assert first != second
    model.apply_pose(first)
    assert model.render().getpixel((3, 2)) == (255, 0, 0, 255)
    model.apply_pose(second)
    assert model.render().getpixel((5, 2)) == (255, 0, 0, 255)


def test_staged_selection_cannot_be_repainted_before_confirmation():
    source = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()
    body = source.split('    def slimer_paint(self,x,y,erase):', 1)[1].split('    def slimer_preview(self):', 1)[0]
    assert "getattr(self, '_slimer_pending_part', None) is not None" in body
    assert body.index('return') < body.index('self.slimer_selection.paint(')
