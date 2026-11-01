"""Phase 102 must change timeline presentation, never editing or drag logic."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'friendly_animator.py'
SKIN = ROOT / 'studio' / 'ui_pixel_theme.py'


def test_restyle_targets_only_existing_pose_widgets():
    source, css = SRC.read_text(), SKIN.read_text()
    names = ('pixelTimelineHeading', 'pixelPoseTimeline',
             'pixelTimelineTimingCaption', 'pixelTimelineDuration',
             'pixelTimelineSavePose', 'pixelTimelineRestorePose',
             'pixelTimelineDuplicatePose', 'pixelTimelinePreviousPose',
             'pixelTimelineNextPose', 'pixelTimelineInsertPose',
             'pixelTimelineCopyPose', 'pixelTimelineRemovePose',
             'pixelTimelineShiftLeft', 'pixelTimelineShiftRight',
             'pixelTimelineImportPose')
    for name in names:
        assert name in source, f'{name} missing from existing widget setup'
        assert name in css, f'{name} missing from visual stylesheet'
    assert 'PIXEL_THEME_QSS += PHASE102_TIMELINE_CHROME_QSS' in css
    assert 'setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)' in source
    assert 'self.timeline.model().rowsMoved.connect(self._timeline_rows_moved)' in source
    assert 'self.timeline.currentRowChanged.connect(self.load_frame)' in source
    assert 'self.duration.valueChanged.connect(self.change_duration)' in source


def test_stylesheet_stays_css_only():
    syntax = ast.parse(SKIN.read_text())
    assert not any(isinstance(node, (ast.ClassDef, ast.FunctionDef,
                                     ast.AsyncFunctionDef, ast.Import, ast.ImportFrom))
                   for node in ast.walk(syntax))


def test_behavior_methods_identical_to_approved_phase101():
    module = ast.parse(SRC.read_text())
    cls = next(node for node in module.body
               if isinstance(node, ast.ClassDef) and node.name == 'Suite')
    funcs = {node.name: hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest()
             for node in cls.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
             and node.name != '__init__'}
    frozen = json.loads((ROOT / 'tests' / 'phase102_phase101_method_hashes.json').read_text())
    assert funcs == frozen


def test_signal_connection_count_unchanged():
    ast_tree = ast.parse(SRC.read_text())
    cls = next(node for node in ast_tree.body if isinstance(node, ast.ClassDef) and node.name == 'Suite')
    init = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == '__init__')
    signal_links = [node for node in ast.walk(init) if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute) and node.func.attr == 'connect']
    assert len(signal_links) == 73  # Exact Phase101 baseline constructor count
