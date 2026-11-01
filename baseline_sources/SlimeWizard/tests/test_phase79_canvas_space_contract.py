"""Phase 79 non-GUI regression: removed redundant top workflow rows.

Runs without PySide6 so we protect the source cleanup in every environment.
"""
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'friendly_animator.py'


def test_buddy_station_and_readiness_button_not_added_to_canvas_layout():
    source = SOURCE.read_text(encoding='utf-8')
    assert 'self.buddy_station=' not in source
    assert 'self.check_button=' not in source
    assert "ml.addWidget(self.buddy_toggle)" not in source
    assert 'modebar.addWidget(self.buddy_toggle)' in source
    assert "self.buddy_toggle.setObjectName('topSlimeBuddyToggle')" in source
    assert 'self.refresh_buddy()' in source


def test_core_import_and_checks_remain_implemented_without_unneeded_controls():
    source = SOURCE.read_text(encoding='utf-8')
    assert "('Import PNG assets',self.import_assets)" in source
    assert 'def show_technical_checks(self):' in source
    assert 'check_animation(self.model,self.anim.currentText())' in source
    assert "self.buddy_toggle.toggled.connect(lambda enabled:self.settings.setValue('slime_buddy_enabled',enabled))" in source
    # Phase 101 removes the duplicate dock checkbox; the top toggle is the only switch.
    assert 'self.buddy_dock_toggle=' not in source
    assert "modebar.addWidget(self.buddy_toggle)" in source


def test_buddy_text_is_contextual_and_not_visual_criticism():
    source = SOURCE.read_text(encoding='utf-8')
    assert 'def refresh_buddy(self,*_):' in source
    assert 'if self.slimer_toggle.isChecked():' in source
    assert 'elif not self.model.parts:' in source
    assert 'Your design is your choice.' in source
    assert 'self.buddy_station.currentText()' not in source
