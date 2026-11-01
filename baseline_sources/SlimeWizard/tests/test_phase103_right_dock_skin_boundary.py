"""Phase 103: right dock uses presentation-only changes against Phase 102."""
import ast
import collections
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'friendly_animator.py'
SKIN = ROOT / 'studio' / 'ui_pixel_theme.py'
BASELINE = ROOT / 'tests' / 'phase103_phase102_baseline.json'


def _suite_init_and_methods():
    module = ast.parse(SRC.read_text(encoding='utf-8'))
    suite = next(n for n in module.body if isinstance(n, ast.ClassDef) and n.name == 'Suite')
    init = next(n for n in suite.body if isinstance(n, ast.FunctionDef) and n.name == '__init__')
    methods = {n.name: hashlib.sha256(ast.dump(n, include_attributes=False).encode()).hexdigest()
               for n in suite.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
               and n.name != '__init__'}
    return init, methods


def test_existing_editor_methods_and_connections_are_identical():
    init, methods = _suite_init_and_methods()
    frozen = json.loads(BASELINE.read_text())
    assert methods == frozen['method_hashes']
    connections = [n for n in ast.walk(init) if isinstance(n, ast.Call)
                   and isinstance(n.func, ast.Attribute) and n.func.attr == 'connect']
    assert len(connections) == frozen['signal_connections'] == 73


def test_existing_gui_controls_not_added_or_removed():
    init, _ = _suite_init_and_methods()
    frozen = json.loads(BASELINE.read_text())
    constructors = collections.Counter(n.func.id for n in ast.walk(init) if isinstance(n, ast.Call)
                                       and isinstance(n.func, ast.Name)
                                       and n.func.id in frozen['widget_constructor_counts'])
    assert dict(constructors) == frozen['widget_constructor_counts']


def test_right_side_skin_is_css_only_and_targets_original_widgets():
    css_text = SKIN.read_text(encoding='utf-8')
    source = SRC.read_text(encoding='utf-8')
    assert 'PIXEL_THEME_QSS += PHASE103_RIGHT_DOCK_QSS' in css_text
    theme_ast = ast.parse(css_text)
    assert not any(isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef,
                                  ast.Import, ast.ImportFrom)) for n in ast.walk(theme_ast))
    for name in ('pixelBuddyWorkspaceHeading', 'pixelBuddyMascot', 'pixelBuddySpeechBubble',
                 'pixelBuddyProductionHeading', 'pixelBuddyProductionExplainer',
                 'buddyProductionStatus', 'pixelBuddyHandoffLabel', 'pixelAnimationPreviewHeading',
                 'animationPreviewCollapseButton', 'pixelSlimerPreviewHeading',
                 'pixelCreaturePreviewHeading', 'pixelSlimerCleanPreview',
                 'pixelFramePreviewImage', 'pixelFramePreviewScroll', 'pixelPreviewZoomOut',
                 'pixelPreviewZoomIn', 'pixelPreviewZoomFit', 'pixelPreviewPlayButton',
                 'pixelPreviewSpeedHeading', 'pixelPreviewSpeedSelect', 'pixelPreviewLoopCheck'):
        assert name in source, f'{name} missing from existing controls'
        assert name in css_text, f'{name} missing from right-side theme'
    assert 'not connected in this build' in source
    assert "self.buddy_toggle=QCheckBox('🌱 Slime Buddy ON / OFF')" in source
    assert source.count("QCheckBox('🌱 Slime Buddy ON / OFF')") == 1


def test_original_preview_and_production_boundaries_stay_separate():
    source = SRC.read_text(encoding='utf-8')
    for unchanged in (
        'self.right_splitter.addWidget(self.buddy_workspace_panel)',
        'self.right_splitter.addWidget(self.animation_preview_section)',
        'self.animation_preview_toggle.clicked.connect(self.toggle_animation_preview)',
        'self.play.toggled.connect(self.play_toggled)',
        'self.speed.currentIndexChanged.connect(self.restart_playback)',
        'self.loop.toggled.connect(self.restart_playback)',
        'self.right_splitter.setSizes(initial_right_sizes)',
    ):
        assert unchanged in source
