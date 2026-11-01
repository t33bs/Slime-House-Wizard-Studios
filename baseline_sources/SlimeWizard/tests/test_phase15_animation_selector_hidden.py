from pathlib import Path


def test_choose_animation_ui_removed_without_disconnecting_internal_state():
    source = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text(encoding='utf-8')
    assert "QPushButton('▾ Choose Animation')" not in source
    assert 'ml.addWidget(self.anim)' not in source
    assert 'self.anim.hide()' in source
    assert 'self.anim.currentTextChanged.connect(self.change_anim)' in source
    assert 'self.anim.addItems(available_animation_names(self.model))' in source
