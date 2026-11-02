"""Exact RGB/alpha reference sampling; test without installing GUI libraries."""
import ast
from pathlib import Path
from types import SimpleNamespace
from PIL import Image
from studio.chameleon_tool import stamp_2x2, sample_2x2

ROOT=Path(__file__).resolve().parents[1]


def _extract(name, filename, classname=None, namespace=None):
    code=Path(filename).read_text(encoding='utf-8')
    tree=ast.parse(code)
    nodes=tree.body if classname is None else next(
        n.body for n in tree.body if isinstance(n,ast.ClassDef) and n.name==classname)
    method=next(n for n in nodes if isinstance(n,ast.FunctionDef) and n.name==name)
    ns=dict(namespace or {})
    exec(compile(ast.Module(body=[method],type_ignores=[]),str(filename),'exec'),ns)
    return ns[name]


def test_actual_preview_pixel_mapping_with_padding_capped_zoom_and_outside():
    convert=_extract('reference_pixel_from_preview',ROOT/'studio/reference_viewer.py')
    # Tiny 4x3 image, 4x nearest-neighbor preview centered in 240x220 label.
    assert convert(112,104,(240,220),(16,12),(4,3))==(0,0)
    assert convert(127,115,(240,220),(16,12),(4,3))==(3,2)
    for pos in [(111,110),(128,110),(120,103),(120,116),(-2,110)]:
        assert convert(*pos,(240,220),(16,12),(4,3)) is None
    # Preview size clamped to nonintegral scale: mapping uses actual pixmap width.
    assert convert(1023,511,(1024,512),(1024,512),(4096,2048))==(4092,2044)
    assert convert(0,0,(1024,512),(1024,512),(4096,2048))==(0,0)
    assert convert(0,0,(0,512),(1024,512),(4096,2048)) is None


class FakeTool:
    def __init__(self, initial): self.value=initial
    def currentText(self):return self.value
    def setCurrentText(self, value):self.value=value


class FakeStatus:
    def __init__(self):self.message=''
    def showMessage(self,msg,*_):self.message=msg


class FakeEditor:
    def __init__(self, tool):
        self.tool=FakeTool(tool)
        self.paint_color=(1,2,3,255)
        self.chameleon_sample=None
        self.status=FakeStatus()
        self._dirty=False
        self.history=[]
    def statusBar(self):return self.status


def test_reference_sample_exact_rgba_one_shot_and_transparent_do_not_modify_source():
    ref=Image.new('RGBA',(6,6),(0,0,0,0))
    ref.putpixel((2,3),(111,42,199,113))
    data=ref.tobytes()
    callback=_extract('sample_reference_at',ROOT/'studio/app.py','MainWindow',{'sample_2x2':sample_2x2})
    editor=FakeEditor('Eyedropper')
    assert not callback(editor,ref,0,0)
    assert editor.tool.currentText()=='Eyedropper' and editor.paint_color==(1,2,3,255)
    assert callback(editor,ref,2,3)
    assert editor.paint_color==(111,42,199,113)
    assert editor.tool.currentText()=='Pencil'
    assert not callback(editor,ref,2,3)  # Pencil cannot sample a reference
    assert ref.tobytes()==data and not editor._dirty and not editor.history


def test_chameleon_reference_resamples_without_stamp_and_preserves_alpha():
    ref=Image.new('RGBA',(5,5),(20,30,40,255))
    colors=[(210,10,10,255),(0,0,0,0),(30,90,120,137),(40,70,100,255)]
    for (x,y),color in zip(((1,1),(2,1),(1,2),(2,2)),colors): ref.putpixel((x,y),color)
    original=ref.tobytes()
    callback=_extract('sample_reference_at',ROOT/'studio/app.py','MainWindow',{'sample_2x2':sample_2x2})
    editor=FakeEditor('Chameleon (2×2)')
    assert not callback(editor,ref,4,4)
    assert editor.chameleon_sample is None
    assert callback(editor,ref,1,1)
    assert editor.chameleon_sample.size==(2,2)
    assert [editor.chameleon_sample.getpixel((x,y)) for y in range(2) for x in range(2)]==colors
    assert editor.tool.currentText()=='Chameleon (2×2)'
    assert callback(editor,ref,0,0)  # re-sample on reference, do not stamp it
    assert editor.chameleon_sample.getpixel((0,0))==(20,30,40,255)
    assert callback(editor,ref,1,1)
    canvas=Image.new('RGBA',(8,8))
    stamp_2x2(canvas,editor.chameleon_sample,4,5)
    assert [canvas.getpixel((4+x,5+y)) for y in range(2) for x in range(2)]==colors
    assert ref.tobytes()==original and not editor._dirty and not editor.history
