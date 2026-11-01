"""Export must produce usable pixel artwork, not an apparently empty source."""
import ast
import tempfile
from pathlib import Path
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


class Status:
    def __init__(self):self.value=''
    def setText(self,value):self.value=value


class Dialog:
    path=None
    called=False
    @classmethod
    def getSaveFileName(cls,*args):
        cls.called=True
        return (str(cls.path), 'PNG')


source=Path(__file__).resolve().parents[1]/'friendly_animator.py'
tree=ast.parse(source.read_text(encoding='utf8'))
function=next(node for node in ast.walk(tree)
              if isinstance(node,ast.FunctionDef) and node.name=='export_asset_for_shs')
scope={'Image':Image,'Path':Path,'QFileDialog':Dialog,'tempfile':tempfile}
exec(compile(ast.Module(body=[function],type_ignores=[]),str(source),'exec'),scope)


class Harness:
    export_asset_for_shs=scope['export_asset_for_shs']
    def __init__(self,size=(128,128)):
        self.model=PetSuiteModel(size)
        self.status=Status()
        self._slimer_pending_part=None
        self.selected=-1


def test_full_canvas_slimer_asset_exports_tight_visible_pixels(tmp_path):
    h=Harness()
    art=Image.new('RGBA',(128,128))
    for y in range(91,95):
        for x in range(31,34):
            art.putpixel((x,y),(170,80,210,255))
    h.model.import_part('Slimer Layer 001',art)
    h.selected=0
    h.model.parts[0]['x']=4
    Dialog.path=tmp_path/'leg.png';Dialog.called=False
    assert h.export_asset_for_shs(),h.status.value
    assert Dialog.called
    with Image.open(Dialog.path) as png:
        assert png.format=='PNG'
        assert png.size==(3,4),png.size
        assert png.convert('RGBA').getpixel((0,0))==(170,80,210,255)
    assert len(h.model.parts)==1


def test_untransformed_small_import_preserves_native_padding(tmp_path):
    h=Harness()
    art=Image.new('RGBA',(12,14))
    art.putpixel((3,4),(40,200,90,117))
    h.model.import_part('Small sprite',art);h.selected=0
    Dialog.path=tmp_path/'small.png'
    assert h.export_asset_for_shs(),h.status.value
    with Image.open(Dialog.path) as exported:
        assert exported.size==(12,14)
        assert exported.convert('RGBA').tobytes()==art.tobytes()


def test_rotated_asset_matches_selected_render_only(tmp_path):
    h=Harness()
    sprite=Image.new('RGBA',(19,17))
    for y in range(3,11):
        for x in range(5,8):sprite.putpixel((x,y),(255,120,10,255))
    h.model.import_part('Sword',sprite)
    h.model.parts[0]['x']=40
    h.model.parts[0]['y']=31
    h.model.rotate_part(0,90)
    h.selected=0
    expected=h.model.render_part(0,h.model.resolved_pose()[0])
    expected=expected.crop(expected.getchannel('A').getbbox())
    Dialog.path=tmp_path/'turned.png'
    assert h.export_asset_for_shs(),h.status.value
    with Image.open(Dialog.path) as export:
        assert export.size==expected.size
        assert export.convert('RGBA').tobytes()==expected.tobytes()


def test_empty_offcanvas_source_does_not_create_blank_file(tmp_path):
    h=Harness()
    art=Image.new('RGBA',(12,12))
    art.putpixel((3,4),(120,210,30,255))
    h.model.import_part('Far away',art)
    h.model.parts[0]['x']=1000
    h.selected=0
    Dialog.path=tmp_path/'must_not_exist.png';Dialog.called=False
    assert not h.export_asset_for_shs()
    assert not Dialog.path.exists()
    assert not Dialog.called
    assert 'no visible pixels' in h.status.value


def test_pending_move_blocks_export_and_preserves_existing_file(tmp_path):
    h=Harness()
    art=Image.new('RGBA',(12,12));art.putpixel((2,2),(255,0,0,255))
    h.model.import_part('still pending',art)
    h.selected=0
    h._slimer_pending_part=h.model.parts[0]
    Dialog.path=tmp_path/'keep.png';Dialog.path.write_bytes(b'old contents')
    Dialog.called=False
    assert not h.export_asset_for_shs()
    assert Dialog.path.read_bytes()==b'old contents'
    assert not Dialog.called
