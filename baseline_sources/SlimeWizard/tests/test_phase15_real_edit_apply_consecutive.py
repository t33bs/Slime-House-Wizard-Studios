"""Production Edit Selection and Apply Move exercised end-to-end without Qt."""
import ast
from pathlib import Path
from contextlib import contextmanager
from PIL import Image, ImageChops
from studio.pet_suite_model import PetSuiteModel

@contextmanager
def blocked_signals(_):
    yield

class Toggle:
    def __init__(self, checked=True): self.checked=checked; self.enabled=True
    def isChecked(self): return self.checked
    def setEnabled(self, value): self.enabled=value
    def setChecked(self, value): self.checked=value

class Widget:
    def __init__(self): self.value=None; self.items=[]
    def setText(self, value): self.value=value
    def addItem(self, value): self.items.append(value)
    def setCurrentRow(self, value): self.value=value
    def setValue(self, value): self.value=value
    def currentText(self): return 'green'

class Selection:
    def __init__(self, source, mask): self.source=source.copy(); self.mask=mask
    @staticmethod
    def empty(source): return Selection(source, Image.new('L', source.size))

class History:
    def __init__(self): self.past=[]; self.future=[]
    def record(self, model): self.past.append(model.snapshot())

NAMES = ('_slimer_layered_erase_plan', '_slimer_transformed_erase_plan',
         '_slimer_original_erase_safe', '_slimer_erase_original_layers',
         '_slimer_visible_selection_mask', 'slimer_create_editable_layer',
         'slimer_apply_move_to_pose', 'slimer_clear', 'remember')
path=Path(__file__).resolve().parents[1]/'friendly_animator.py'
tree=ast.parse(path.read_text(encoding='utf-8'))
methods={node.name:node for node in ast.walk(tree) if isinstance(node,ast.FunctionDef)}
scope={'Image':Image,'ImageChops':ImageChops,'blocked_signals':blocked_signals,'SlimerSelection':Selection}
exec(compile(ast.Module(body=[methods[name] for name in NAMES],type_ignores=[]),str(path),'exec'),scope)

class Harness:
    def __init__(self):
        self.model=PetSuiteModel((16,16)); self.history=History()
        self.status=Widget();self.assets=Widget();self.slimer_move_original=Toggle()
        self.slimer_drag_toggle=Toggle(False);self.slimer_phase_picker=Widget()
        self.slimer_dx=Widget();self.slimer_dy=Widget();self.slimer_turn=Widget();self.slimer_scale=Widget()
        self.canvas=type('Canvas',(),{})()
        self.slimer_selection=None;self.slimer_selection_undo=[];self.slimer_selection_redo=[]
        self._slimer_pending_layer=None;self._slimer_pending_part=None
        self._slimer_pending_source=None;self._slimer_pending_mask=None
        self._slimer_pending_move_original=None;self._slimer_redo_transaction=None
        self._pose_draft_dirty=False;self._pose_draft_key=None
    def refresh(self): pass
    def mark_pose_draft(self): pass
    def _slimer_sync_numeric_values(self): pass

for name in NAMES:
    setattr(Harness,name,scope[name])

def test_three_consecutive_real_edit_selection_apply_move():
    h=Harness(); base=Image.new('RGBA',(16,16))
    for xy, color in [((2,2),(250,20,20,255)),((5,5),(20,250,20,255))]: base.putpixel(xy,color)
    h.model.import_part('Base',base)
    for number,(sx,sy,dx,dy) in enumerate(((2,2,8,8),(5,5,11,11),(8,8,13,13)),1):
        mask=Image.new('L',h.model.size);mask.putpixel((sx,sy),255)
        h.slimer_selection=Selection(h.model.render(),mask)
        assert h.slimer_create_editable_layer(),h.status.value
        assert len(h.model.parts)==number+1
        pending=h._slimer_pending_part
        pending['x']=dx-sx;pending['y']=dy-sy
        assert h.slimer_apply_move_to_pose(),h.status.value
        assert h._slimer_pending_part is None
        assert h.model.render().getpixel((sx,sy))[3]==0
        assert h.model.render().getpixel((dx,dy))[3]==255
        assert h.slimer_selection.mask.getbbox() is None
    assert h.model.render().getpixel((13,13))==(250,20,20,255)
    assert h.model.render().getpixel((11,11))==(20,250,20,255)
    assert len(h.model.parts)==4


def test_copy_mode_repeated_edit_apply_preserves_sources():
    h=Harness();h.slimer_move_original.setChecked(False)
    base=Image.new('RGBA',(16,16));base.putpixel((2,2),(42,80,210,255))
    h.model.import_part('Base',base)
    for dest in (8,12):
        mask=Image.new('L',h.model.size);mask.putpixel((2,2),255)
        h.slimer_selection=Selection(h.model.render(),mask)
        assert h.slimer_create_editable_layer(),h.status.value
        h._slimer_pending_part['x']=dest-2
        h._slimer_pending_part['y']=dest-2
        assert h.slimer_apply_move_to_pose(),h.status.value
        assert h.model.render().getpixel((2,2))==(42,80,210,255)
        assert h.model.render().getpixel((dest,dest))==(42,80,210,255)
    assert len(h.model.parts)==3


def test_failed_apply_preserves_pending_source_and_allows_retry():
    h=Harness();base=Image.new('RGBA',(16,16));base.putpixel((2,2),(210,40,70,255))
    h.model.import_part('Base',base)
    mask=Image.new('L',h.model.size);mask.putpixel((2,2),255)
    h.slimer_selection=Selection(h.model.render(),mask)
    assert h.slimer_create_editable_layer(),h.status.value
    pending=h._slimer_pending_part
    pending['x']=40;pending['y']=40
    assert h.slimer_apply_move_to_pose() is False
    assert h._slimer_pending_part is pending
    assert h.model.render().getpixel((2,2))==(210,40,70,255)
    pending['x']=6;pending['y']=6
    assert h.slimer_apply_move_to_pose(),h.status.value
    assert h.model.render().getpixel((8,8))==(210,40,70,255)
    assert h.model.render().getpixel((2,2))[3]==0


def test_resized_staged_layer_then_move_its_pixels_again():
    """Resized destination must remain a valid source for a later Slimer move."""
    h=Harness(); base=Image.new('RGBA',(16,16));base.putpixel((2,2),(255,90,40,255))
    h.model.import_part('Base',base)
    mask=Image.new('L',h.model.size);mask.putpixel((2,2),255)
    h.slimer_selection=Selection(h.model.render(),mask)
    assert h.slimer_create_editable_layer(),h.status.value
    idx=h._slimer_pending_layer
    h.model.resize_part(idx,32,32)
    h._slimer_pending_part['x']=0;h._slimer_pending_part['y']=0
    assert h.slimer_apply_move_to_pose(),h.status.value
    # The full-canvas source was resized 2x, so the source pixel is now at (4,4).
    assert h.model.render().getpixel((4,4))[3]==255
    mask=Image.new('L',h.model.size)
    for y in (4,5):
        for x in (4,5):mask.putpixel((x,y),255)
    h.slimer_selection=Selection(h.model.render(),mask)
    assert h.slimer_create_editable_layer(),h.status.value
    h._slimer_pending_part['x']=5
    assert h.slimer_apply_move_to_pose(),h.status.value
    assert h.model.render().getpixel((4,4))[3]==0
    assert h.model.render().getpixel((9,4))[3]==255
