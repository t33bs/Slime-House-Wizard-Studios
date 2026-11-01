"""Windows PySide6: no reference content UI, real sprite imports and preview survive."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest
pytestmark = pytest.mark.usefixtures('isolate_gui_recovery')
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite

def test_reference_ui_absent_but_actual_previews_and_artwork_imports_present():
    app=QApplication.instance() or QApplication([])
    w=Suite()
    w.confirm_unsaved_projects=lambda *args,**kwargs: True
    w.show()
    app.processEvents()
    try:
        assert not hasattr(w,'uploaded_reference_toggle')
        assert not hasattr(w,'reference_timer')
        assert w.slimer_preview_label is not None
        assert w.preview is not None
        assert w.library_import.text()=='Import Asset'
        assert w.comparison_toggle.text()=='👁 Hide previews'
    finally:
        w.close()
