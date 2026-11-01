"""Exercise Phase 76 handle geometry without importing PySide6.

Qt GUI tests separately verify actual drawn controls, signals and mouse events.
"""
import ast
import math
from pathlib import Path

CODE=Path(__file__).resolve().parents[1].joinpath('friendly_animator.py').read_text()
TREE=ast.parse(CODE)
CANVAS=next(c for c in TREE.body if isinstance(c,ast.ClassDef) and c.name=='DragCanvas')
NAMES=('_asset_transform_geometry','_asset_handle_screen','_asset_transform_hit')
METHODS={n.name:n for n in CANVAS.body if isinstance(n,ast.FunctionDef)}
from studio.viewport_handles import visible_handle_position
SCOPE={'math':math, 'visible_handle_position':visible_handle_position}
exec(compile(ast.Module(body=[METHODS[n] for n in NAMES],type_ignores=[]),'<handle math>','exec'),SCOPE)

class FakeCanvas:
    def __init__(self,angle=0,zoom=3):
        self.angles={0:angle}
        self.zoom=zoom
        self.slimer_active=False
        self.asset_controls_enabled=True
        self.selected=0
        self.asset_handle_mode='move_x'
        self.parts=[{'visible':True}]
        self.handle_panel=type('Panel', (), {'isVisible':lambda _:False})()
    def _selected_rotation_geometry(self,index):
        assert index==0
        return (41,51),(41,37),(40,50,42,52)
    def _geometry(self):
        return self.zoom,10,20
    def width(self):return 650
    def height(self):return 550

for n in NAMES:
    setattr(FakeCanvas,n,SCOPE[n])

class Point:
    def __init__(self,x,y):self._x=x;self._y=y
    def x(self):return self._x
    def y(self):return self._y


def test_four_distinct_handles_near_art_and_not_the_whole_canvas():
    canvas=FakeCanvas()
    corners,h,pivot=canvas._asset_transform_geometry(0)
    assert pivot==(41,51)
    assert set(h)=={'move_x','move_y','rotate','resize'}
    assert h['resize'][0] > 42 and h['resize'][1] > 52
    assert h['move_x'][0] > 42
    assert h['move_y'][1] > 52
    assert h['rotate']==(41,37)
    assert corners==[(40,50),(42,50),(42,52),(40,52)]


def test_handles_follow_rotation_and_zoom():
    canvas=FakeCanvas(angle=90,zoom=2)
    corners,h,pivot=canvas._asset_transform_geometry(0)
    assert h['move_x'][1] > 52  # side handle follows the rotated edge
    assert h['move_y'][0] < 40   # bottom handle follows the rotated edge
    canvas.zoom=4
    _,h2,_=canvas._asset_transform_geometry(0)
    assert h2['move_x'][1] < h['move_x'][1]  # fixed-size widget offset


def test_handles_use_screen_coordinate_hit_testing_and_hide_when_disabled():
    canvas=FakeCanvas()
    _,h,_=canvas._asset_transform_geometry(0)
    for action,(x,y) in h.items():
        canvas.asset_handle_mode=action
        px, py = canvas._asset_handle_screen(action)
        assert canvas._asset_transform_hit(Point(px,py))==action
    canvas.asset_handle_mode='rotate'
    canvas.asset_controls_enabled=False
    assert canvas._asset_transform_hit(Point(10+h['rotate'][0]*3,20+h['rotate'][1]*3)) is None
    canvas.asset_controls_enabled=True
    canvas.slimer_active=True
    assert canvas._asset_transform_hit(Point(10+h['rotate'][0]*3,20+h['rotate'][1]*3)) is None
