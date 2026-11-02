"""Import-free regression guards for the unwanted idle canvas bubble."""
from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]


def test_canvas_hover_tooltip_filter_only_covers_artwork_canvases():
    src = (ROOT / 'main.py').read_text(encoding='utf-8')
    tree = ast.parse(src)
    guard = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'CanvasHoverTipGuard')
    fn = next(n for n in guard.body if isinstance(n, ast.FunctionDef) and n.name == 'eventFilter')
    body = ast.get_source_segment(src, fn)
    assert 'QEvent.Type.ToolTip' in body
    assert 'QToolTip.hideText()' in body
    assert 'event.accept()' in body
    assert 'return True' in body
    assert 'QEvent.Type.Enter' in body
    # No blanket application-wide tooltip suppression: hover help on controls is useful.
    assert "(self.studio.canvas, self.wizard.canvas)" in src
    assert "editing_canvas.setToolTip('')" in src
    assert 'editing_canvas.installEventFilter(self._canvas_tip_guard)' in src
    assert 'QApplication.instance().installEventFilter' not in src
    assert "self.studio.external_save_button.setToolTip(" in src


def test_previous_ui_and_save_fixes_are_not_modified():
    src = (ROOT / 'main.py').read_text(encoding='utf-8')
    assert 'self.studio.linked_png_saved.connect(self._finish_shs_frame_handoff)' in src
    assert 'self.wizard.reload_shs_edit()' in src
    assert 'self.wizard._shs_pose_id = None' in src
    shs = (ROOT / 'studio/app.py').read_text(encoding='utf-8')
    assert "m.tool.setCurrentText('Pencil')" in shs
    assert "('P',self.activate_universal_brush),('B',self.activate_paint_bucket)" in shs
    wizard = (ROOT / 'shws_wizard/friendly_animator.py').read_text(encoding='utf-8')
    assert 'pixelCanvasTimelineSplitter' in wizard
    assert 'Slimer Layer' in wizard
    assert "self.buddy_bubble.setText(tip)" in wizard
