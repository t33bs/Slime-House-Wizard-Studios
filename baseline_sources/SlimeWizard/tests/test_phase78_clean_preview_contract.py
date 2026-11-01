"""Clean Slimer Preview is computed from live model pixels before UI overlays."""
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()


def test_clean_canvas_preview_uses_live_render_without_editor_highlights():
    body = SOURCE.split('    def refresh(self):',1)[1].split('    def _reset_slimer_for_project_change',1)[0]
    assert body.index('live_render=self.model.render()') < body.index('if self.onion.isChecked():')
    assert 'composed=live_render' in body
    assert 'if composed is live_render:' in body
    assert 'composed=live_render.copy()' in body
    assert body.index('live_render=self.model.render()') < body.index('marker.putalpha(')
    assert 'self.slimer_preview_label.setPixmap(pixmap(live_render, 132))' in body
    assert 'self.slimer_preview_label.setPixmap(pixmap(confirmed_slimer_preview, 132))' not in body
    assert 'self.refresh_preview(live_render)' in body


def test_compact_menu_is_still_on_canvas_not_left_sidebar():
    assert 'self.handle_panel = QFrame(self)' in SOURCE
    assert 'self.handle_menu_details.hide()' in SOURCE
    assert 'self.handle_mode_picker.addItem(\'R — Rotate in degrees\', \'rotate\')' in SOURCE
