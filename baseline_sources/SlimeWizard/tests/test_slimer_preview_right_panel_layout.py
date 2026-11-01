"""Regression checks for the requested UI placement and preset reference removal."""
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'friendly_animator.py'


def test_slimer_preview_is_added_to_right_panel_only():
    source = SOURCE.read_text(encoding='utf-8')
    assert "preview_body_layout.addWidget(self.slimer_preview_label)" in source
    assert "ll.addWidget(self.slimer_preview_label)" not in source
    assert source.index("self.slimer_preview_label=QLabel") < source.index("preview_body_layout.addWidget(self.slimer_preview_label)")


def test_reference_only_ui_removed_while_real_previews_remain():
    source = SOURCE.read_text(encoding='utf-8')
    for obsolete in (
        'uploaded_reference_toggle', 'uploaded_reference_image',
        'load_uploaded_reference', 'render_uploaded_reference',
        'Show my animation reference', 'Animation Reference Viewer',
        'Load PNG / GIF / APNG / sheet',
    ):
        assert obsolete not in source
    assert "preview_body_layout.addWidget(self.slimer_preview_label)" in source
    assert "preview_body_layout.addWidget(self.preview_scroll)" in source
    assert 'Import PNG assets' in source
    assert 'Import Asset' in source
