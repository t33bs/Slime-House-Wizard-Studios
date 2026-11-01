"""Phase 101 changes presentation only, except removal of duplicate Buddy checkbox."""
import ast
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'friendly_animator.py'
CSS = ROOT / 'studio' / 'ui_pixel_theme.py'


def test_single_buddy_switch_and_canvas_chrome_present():
    source = SRC.read_text()
    skin = CSS.read_text()
    assert "self.buddy_toggle.setObjectName('topSlimeBuddyToggle')" in source
    assert "self.buddy_toggle.toggled.connect(self.refresh_buddy)" in source
    assert "self.buddy_toggle.toggled.connect(lambda enabled:self.settings.setValue('slime_buddy_enabled',enabled))" in source
    assert 'buddy_dock_toggle' not in source
    for selector in ('pixelCanvasRegion', 'pixelCanvasHeading', 'pixelMainCanvas',
                     'pixelCanvasFitButton', 'pixelZoomReadout',
                     'pixelWorkspaceTabs', 'pixelWorkspaceAddButton'):
        assert selector in source
    for selector in ('pixelCanvasRegion', 'pixelCanvasHeading',
                     'pixelCanvasFitButton', 'pixelZoomReadout',
                     'pixelWorkspaceTabs', 'pixelWorkspaceAddButton'):
        assert selector in skin
    assert 'PIXEL_THEME_QSS += PHASE101_CENTER_CHROME_QSS' in skin


def test_pixel_skin_is_data_only():
    module = ast.parse(CSS.read_text())
    assert not any(isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom))
                   for n in ast.walk(module))


def test_existing_editor_methods_match_phase100_baseline():
    """AST check guards all behavior methods against accidental UI-pass edits."""
    import json
    tree = ast.parse(SRC.read_text())
    suite = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Suite')
    current = {n.name: hashlib.sha256(ast.dump(n, include_attributes=False).encode()).hexdigest()
               for n in suite.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
               and n.name != '__init__'}
    expected = json.loads((ROOT / 'tests' / 'phase101_phase100_method_hashes.json').read_text())
    assert current == expected
