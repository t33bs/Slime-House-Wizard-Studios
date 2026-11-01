"""Phase 100 must not alter application operations, callbacks or controls."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def test_phase100_asset_styling_selectors_and_existing_controls():
    text = (ROOT / 'friendly_animator.py').read_text()
    skin = (ROOT / 'studio' / 'ui_pixel_theme.py').read_text()
    for name in ('pixelAssetLibraryList', 'pixelActiveAssetLabel',
                 'pixelLeftToolsHeading', 'pixelAssetsHeading',
                 'pixelSlimerHeading', 'pixelCleanerHeading'):
        assert name in text
        assert name in skin
    for label in ('Import Asset', 'Export for SHS', 'Remove asset from this pose',
                  'Activate Slimer Tool', 'Activate Slime Cleaner',
                  '✓ Apply Move • Continue Selecting'):
        assert label in text
    assert 'PIXEL_THEME_QSS += PHASE100_LEFT_PANEL_QSS' in skin


def test_phase100_stylesheet_is_syntax_independent_of_logic():
    """Pure styling module should have no callback/signal wiring."""
    tree = ast.parse((ROOT / 'studio' / 'ui_pixel_theme.py').read_text())
    assert not any(isinstance(n, (ast.FunctionDef, ast.ClassDef, ast.Import, ast.ImportFrom))
                   for n in ast.walk(tree))
