"""Build 1.3 tests: independent native pixels, Save As, and resize affordances."""
from pathlib import Path
from PIL import Image
from studio.chameleon_tool import sample_2x2, stamp_2x2
import pytest
import ast

ROOT=Path(__file__).resolve().parents[1]


def test_chameleon_copies_exact_native_rgba_and_undo_safe_input():
    src=Image.new('RGBA',(8,8),(0,0,0,0))
    colors=[(234,61,80,255),(0,0,0,0),(40,90,160,180),(20,120,80,255)]
    for (x,y),value in zip(((1,1),(2,1),(1,2),(2,2)),colors):
        src.putpixel((x,y),value)
    source_before=src.tobytes()
    sample=sample_2x2(src,1,1)
    dst=Image.new('RGBA',(8,8),(70,80,90,200))
    dst_before=dst.tobytes()
    stamp_2x2(dst,sample,5,5)
    assert src.tobytes()==source_before
    assert [dst.getpixel((5+x,5+y)) for y in range(2) for x in range(2)]==colors
    assert dst.getpixel((0,0))==(70,80,90,200)
    assert dst.tobytes()!=dst_before


@pytest.mark.parametrize('x,y',[(-1,0),(7,0),(0,7),(9,9)])
def test_chameleon_rejects_out_of_bounds(x,y):
    im=Image.new('RGBA',(8,8))
    with pytest.raises(ValueError):sample_2x2(im,x,y)
    with pytest.raises(ValueError):stamp_2x2(im,Image.new('RGBA',(2,2)),x,y)


def test_wizard_has_real_vertical_splitter_and_persistent_sizes():
    path=ROOT/'shws_wizard/friendly_animator.py'
    src=path.read_text(encoding='utf-8')
    tree=ast.parse(src)
    suite=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Suite')
    init=next(n for n in suite.body if isinstance(n,ast.FunctionDef) and n.name=='__init__')
    close=next(n for n in suite.body if isinstance(n,ast.FunctionDef) and n.name=='closeEvent')
    setup=ast.get_source_segment(src,init)
    teardown=ast.get_source_segment(src,close)
    assert 'QSplitter(Qt.Orientation.Vertical,middle)' in setup
    assert "setObjectName('pixelCanvasTimelineSplitter')" in setup
    assert 'setChildrenCollapsible(False)' in setup
    assert 'setHandleWidth(13)' in setup
    assert 'self.canvas_timeline_splitter.addWidget(canvas_region)' in setup
    assert 'self.canvas_timeline_splitter.addWidget(self.timeline_scroll)' in setup
    assert "self.settings.value('canvas_timeline_splitter_sizes',None)" in setup
    assert "self.settings.setValue('canvas_timeline_splitter_sizes',self.canvas_timeline_splitter.sizes())" in teardown
    assert 'setMinimumHeight(205)' in setup
    assert 'setMaximumHeight(420)' in setup
    assert 'setMinimumHeight(124)' in setup
    assert "QSize(82,82)" in setup


def test_left_tool_and_asset_scrollbars_are_larger_and_scoped():
    src=(ROOT/'shws_wizard/friendly_animator.py').read_text(encoding='utf-8')
    stylesheet=(ROOT/'shws_wizard/studio/ui_pixel_theme.py').read_text(encoding='utf-8')
    assert "self.left_tool_scroll.setObjectName('pixelLeftToolsScroll')" in src
    assert 'verticalScrollBar().setMinimumWidth(19)' in src
    for selector in ('QScrollArea#pixelLeftToolsScroll QScrollBar:vertical',
                     'QListWidget#pixelAssetLibraryList QScrollBar:vertical',
                     'QSplitter#pixelCanvasTimelineSplitter::handle:vertical'):
        assert selector in stylesheet
    assert 'width: 19px' in stylesheet
    assert 'min-height: 44px' in stylesheet


def test_separate_save_as_actions_and_frame_hand_back_exist():
    wizard=(ROOT/'shws_wizard/friendly_animator.py').read_text(encoding='utf-8')
    shs=(ROOT/'studio/app.py').read_text(encoding='utf-8')
    host=(ROOT/'main.py').read_text(encoding='utf-8')
    assert 'def save_project_as(self):' in wizard
    assert 'def save_project_as(self):' in shs
    assert 'self._project_paths[project_id]=str(path)' in wizard
    assert 'Save SHS Pose + Return to Wizard' in host
    assert 'self.wizard.reload_shs_edit()' in host
