"""Guard against launcher-only icon configuration."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_wizard_slime_icon_is_applied_to_running_app_and_window():
    source = (ROOT / 'friendly_animator.py').read_text(encoding='utf-8')
    assert 'app.setWindowIcon(wizard_slime_app_icon())' in source
    assert 'self.setWindowIcon(wizard_slime_app_icon())' in source
    assert "getattr(sys, '_MEIPASS', None)" in source
    assert (ROOT / 'studio/assets/wizard_slime.ico').is_file()
