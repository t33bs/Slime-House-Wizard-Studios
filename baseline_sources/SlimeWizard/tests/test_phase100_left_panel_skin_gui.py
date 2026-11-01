"""Windows validation of left panel style, not of new tool behavior."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication, QListWidget, QLabel
from friendly_animator import Suite

@pytest.mark.usefixtures('isolate_gui_recovery')
def test_phase100_left_panel_keeps_assets_and_controls():
    app=QApplication.instance() or QApplication([])
    window=Suite();window.confirm_unsaved_projects=lambda *args, **kwargs: True
    try:
        before=window.model.content_fingerprint()
        assert window.findChild(QListWidget,'pixelAssetLibraryList') is window.assets
        assert window.findChild(QLabel,'pixelActiveAssetLabel') is window.active_asset_label
        assert window.slimer_toggle.isEnabled()
        assert window.cleaner_toggle.isEnabled()
        assert window.library_import.isEnabled()
        assert window.library_export_shs.isEnabled()
        assert window.model.content_fingerprint()==before
    finally:
        window.close()
