"""Phase 99 locks the approved *visual only* boundary.

The Phase 98 editing methods are frozen for this styling stage; any new
production feature or silently rewired button belongs in another phase.
"""
import ast
import hashlib
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / 'friendly_animator.py').read_text(encoding='utf-8')
THEME = (ROOT / 'studio' / 'ui_pixel_theme.py').read_text(encoding='utf-8')
BASELINE_NON_CONSTRUCTOR_SHA256 = 'b3db377fad840bd8f79f661899a1f9a0e9da386e1a8b7dddcdb9407ac324f378'


def _suite_methods():
    root = ast.parse(APP)
    suite = next(node for node in root.body if isinstance(node, ast.ClassDef)
                 and node.name == 'Suite')
    return {node.name: node for node in suite.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}


def test_phase99_does_not_modify_any_editor_behavior_method():
    methods = _suite_methods()
    assert len(methods) == 154
    blob = '\n'.join(ast.dump(node, include_attributes=False)
                     for name, node in sorted(methods.items()) if name != '__init__')
    assert hashlib.sha256(blob.encode()).hexdigest() == BASELINE_NON_CONSTRUCTOR_SHA256


def test_all_existing_editor_signal_connections_preserved():
    # Counted against Phase98, except the two redundant Buddy-dock checkbox
    # synchronization links explicitly retired in Phase101 at user request.
    for signal, count in {
        'clicked': 31, 'toggled': 11, 'currentRowChanged': 2,
        'valueChanged': 4, 'currentTextChanged': 2, 'rowsMoved': 1,
    }.items():
        assert len(re.findall(r'\.' + signal + r'\.connect\(', APP)) == count


def test_theme_is_styling_only_and_covers_existing_buttons():
    assert 'PIXEL_THEME_QSS' in THEME
    for selector in ('QPushButton, QToolButton', 'QPushButton:hover',
                     'QPushButton:checked', 'QPushButton:disabled',
                     'QTabBar::tab:selected', 'QListWidget::item:selected',
                     'QFrame#slimeBuddyProductionWorkspace',
                     'QFrame#collapsibleAnimationPreview'):
        assert selector in THEME
    assert 'clicked.connect' not in THEME
    assert 'toggled.connect' not in THEME
    assert 'setParent(' not in THEME


def test_original_buddy_and_preview_controls_and_real_workflow_are_retained():
    for entry in (
        'self.buddy_toggle=QCheckBox(', 'self.animation_preview_toggle=QPushButton(',
        'self.slimer_apply_move=QPushButton(', 'self.slimer_place_frame_button = button',
        'self.cleaner_toggle=QPushButton(', 'self.timeline=PoseTimelineList(',
        'self.pose_png_import_button=QToolButton()',
        'self.save_project', 'self.export_animated',
        'self.right_splitter=QSplitter(',
    ):
        assert entry in APP, f'Missing existing control: {entry}'
    assert 'production engine not connected' in APP.lower()
    assert "setProperty('uiRole','primary')" in APP
    assert 'PIXEL_THEME_QSS' in APP
