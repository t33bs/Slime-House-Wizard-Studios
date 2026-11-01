"""Phase 81: Apply Move must erase original sources, never its own staged asset."""
import ast
from pathlib import Path
from PIL import Image, ImageChops
from studio.pet_suite_model import PetSuiteModel
from contextlib import contextmanager

@contextmanager
def blocked_signals(_):
    yield

class Toggle:
    def __init__(self, checked=True): self.checked=checked; self.enabled=True
    def isChecked(self): return self.checked
    def setChecked(self, value): self.checked=value
    def setEnabled(self, value): self.enabled=value

class Widget:
    def __init__(self): self.value=None; self.items=[]
    def setText(self, value): self.value=value
    def addItem(self, item): self.items.append(item)
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

names = ('_slimer_layered_erase_plan', '_slimer_transformed_erase_plan',
         '_slimer_original_erase_safe', '_slimer_erase_original_layers',
         '_slimer_visible_selection_mask', 'slimer_create_editable_layer',
         'slimer_apply_move_to_pose', 'slimer_clear', 'remember')
tree = ast.parse((Path(__file__).resolve().parents[1]/'friendly_animator.py').read_text())
methods = {method.name:method for method in ast.walk(tree)
           if isinstance(method, ast.FunctionDef)}
scope = {'Image':Image,'ImageChops':ImageChops,'blocked_signals':blocked_signals,
         'SlimerSelection':Selection}
exec(compile(ast.Module(body=[methods[n] for n in names], type_ignores=[]),'<production editor>','exec'),scope)

class Harness:
    def __init__(self):
        self.model=PetSuiteModel((32,32));self.history=History()
        self.status=Widget();self.assets=Widget()
        self.slimer_toggle=Toggle(True)
        self.slimer_move_original=Toggle(True);self.slimer_drag_toggle=Toggle(False)
        self.slimer_phase_picker=Widget();self.slimer_dx=Widget();self.slimer_dy=Widget()
        self.slimer_turn=Widget();self.slimer_scale=Widget()
        self.canvas=type('Canvas',(),{'slimer_active':True})()
        self.slimer_selection=None;self.slimer_selection_undo=[];self.slimer_selection_redo=[]
        self._slimer_pending_layer=None;self._slimer_pending_part=None
        self._slimer_pending_source=None;self._slimer_pending_mask=None
        self._slimer_pending_move_original=None;self._slimer_redo_transaction=None
        self._pose_draft_dirty=False;self._pose_draft_key=None
    def refresh(self): pass
    def mark_pose_draft(self): pass
    def _slimer_sync_numeric_values(self): pass
    def _show_asset_transform_controls(self, enabled): self.canvas.asset_controls_enabled=enabled

for name in names: setattr(Harness,name,scope[name])


def stage_square(shift):
    h=Harness();base=Image.new('RGBA',(32,32))
    for y in range(10,14):
        for x in range(10,14):base.putpixel((x,y),(210,70,90,255))
    base.putpixel((22,22),(10,180,220,255))  # unselected reference
    h.model.import_part('Swordcat leg',base)
    mask=Image.new('L',h.model.size)
    for y in range(10,14):
        for x in range(10,14):mask.putpixel((x,y),255)
    h.slimer_selection=Selection(h.model.render(),mask)
    assert h.slimer_create_editable_layer(),h.status.value
    h._slimer_pending_part['x']=shift
    return h


def test_overlap_must_not_erase_destination_layer():
    h=stage_square(1)
    staged=h._slimer_pending_part
    before=staged['image'].tobytes()
    assert h.slimer_apply_move_to_pose(),h.status.value
    assert staged['image'].tobytes()==before
    assert h.model.parts[0]['image'].getpixel((11,10))[3]==0
    assert h.model.render().getpixel((10,10))[3]==0
    for x in range(11,15):
        assert h.model.render().getpixel((x,10))==(210,70,90,255)
    assert h.model.render().getpixel((22,22))==(10,180,220,255)


def test_same_location_move_must_not_erase_the_only_visible_copy():
    h=stage_square(0)
    staged=h._slimer_pending_part
    assert h.slimer_apply_move_to_pose(),h.status.value
    assert h.model.parts[0]['image'].getpixel((10,10))[3]==0
    assert staged['image'].getpixel((10,10))[3]==255
    assert h.model.render().getpixel((10,10))==(210,70,90,255)


def test_raw_erase_restores_staged_visibility_even_if_source_throws():
    h=stage_square(1)
    staged=h._slimer_pending_part
    staged['visible']=True
    # The impossible extra canvas pixel cannot be consumed, so the fallback
    # raises. It must still restore the provisional layer's original visibility.
    mask=Image.new('L',h.model.size)
    mask.putpixel((31,31),255)
    try:
        h._slimer_erase_original_layers(mask)
    except RuntimeError:
        pass
    assert staged['visible'] is True


def test_empty_highlight_does_not_switch_to_unrelated_asset_handles():
    h=Harness();h.model.import_part('Swordcat leg',Image.new('RGBA',(32,32)))
    h.slimer_selection=Selection.empty(h.model.render())
    h.selected=0
    assert not h.slimer_create_editable_layer()
    assert 'Nothing highlighted' in h.status.value
    assert h._slimer_pending_part is None
    assert not hasattr(h.canvas,'asset_controls_enabled')
