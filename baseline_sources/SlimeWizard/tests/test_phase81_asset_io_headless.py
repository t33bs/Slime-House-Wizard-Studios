"""Run production Asset Library PNG I/O methods without a Qt installation."""
import ast
from pathlib import Path
from PIL import Image
from studio.pet_suite_model import PetSuiteModel


class Status:
    def __init__(self): self.value=''
    def setText(self, value): self.value=value


class Library:
    def __init__(self): self.items=[];self.row=-1
    def addItem(self, text):self.items.append(text)
    def setCurrentRow(self, row):self.row=row


class FakeDialog:
    in_path=None;out_path=None
    @classmethod
    def getOpenFileNames(cls, *args):
        return ([str(cls.in_path)] if cls.in_path else [],'PNG')
    @classmethod
    def getSaveFileName(cls, *args):
        return (str(cls.out_path) if cls.out_path else '','PNG')


class FakeMessage:
    class StandardButton:
        Yes=1;No=2;Cancel=3
    @classmethod
    def question(cls,*args): return cls.StandardButton.No
    @classmethod
    def warning(cls,*args):raise AssertionError('PNG import must not warn in this test')


tree=ast.parse((Path(__file__).resolve().parents[1]/'friendly_animator.py').read_text())
methods={m.name:m for m in ast.walk(tree) if isinstance(m,ast.FunctionDef)}
scope={'Path':Path,'Image':Image,'QFileDialog':FakeDialog,'QMessageBox':FakeMessage}
exec(compile(ast.Module(body=[methods[n] for n in ('import_assets','export_asset_for_shs')], type_ignores=[]),'<production methods>','exec'),scope)


class Harness:
    import_assets=scope['import_assets']
    export_asset_for_shs=scope['export_asset_for_shs']
    def __init__(self):
        self.model=PetSuiteModel((128,128));self.assets=Library();self.status=Status()
        self._slimer_pending_part=None;self.slimer_selection=None;self.selected=-1
    def remember(self): pass
    def refresh_parent_picker(self): pass
    def refresh(self): pass


def test_import_then_export_native_rgba_png(tmp_path):
    h=Harness()
    source=Image.new('RGBA',(9,11));source.putpixel((4,3),(200,150,40,117))
    input_path=tmp_path/'leg.png';source.save(input_path)
    FakeDialog.in_path=input_path
    assert h.import_assets()
    h.selected=0
    assert len(h.model.parts)==1
    assert h.assets.items==['leg']
    output_path=tmp_path/'shs_export.png';FakeDialog.out_path=output_path
    assert h.export_asset_for_shs(),h.status.value
    with Image.open(output_path) as image:
        assert image.convert('RGBA').tobytes()==source.tobytes()
        assert image.size==source.size
    assert h.model.parts[0]['image'].getpixel((4,3))==(200,150,40,117)


def test_pending_slimer_blocks_import_and_export_without_touching_sources(tmp_path):
    h=Harness();source=Image.new('RGBA',(8,8),(70,80,90,255))
    h.model.import_part('part',source);h.selected=0
    h._slimer_pending_part=h.model.parts[0]
    assert h.import_assets() is False
    assert h.export_asset_for_shs() is False
    assert len(h.model.parts)==1
    assert h.model.originals[0].tobytes()==source.tobytes()
