"""Headless contract: Phase97 is presentation-only, not a second editor."""
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]


def test_blue_buddy_portrait_is_rgba_native_pixel_asset():
    image=Image.open(ROOT/'studio/assets/slime_buddy_blue_portrait.png')
    assert image.mode=='RGBA'
    assert image.size==(176,176)
    assert image.getpixel((0,0))[3]==0


def test_independent_buddy_ui_and_collapse_handlers_exist():
    text=(ROOT/'friendly_animator.py').read_text(encoding='utf-8')
    for required in (
        "self.buddy_workspace_panel=QFrame()",
        "self.animation_preview_body=QWidget()",
        "self.animation_preview_toggle.clicked.connect(self.toggle_animation_preview)",
        "def set_animation_preview_collapsed(self, collapsed, *, announce=True):",
        "self.animation_preview_body.setVisible(not collapsed)",
        "self.settings.setValue('animation_preview_collapsed',collapsed)",
        "self.buddy_production_status=QLabel('● Production engine not connected in this build')",
    ):
        assert required in text
    assert 'def slimer_place_frame(' in text
