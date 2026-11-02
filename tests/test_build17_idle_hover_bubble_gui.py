"""Windows Qt regression for the blank idle-hover dialogue on the canvases."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
pytest.importorskip('PySide6')
from PySide6.QtCore import QEvent, QPoint
from PySide6.QtGui import QHelpEvent
from PySide6.QtWidgets import QApplication, QToolTip
from main import SlimeHouseWizardStudios


def test_both_canvas_hover_tooltips_blocked_normal_help_preserved():
    app = QApplication.instance() or QApplication([])
    host = SlimeHouseWizardStudios()
    host.wizard.confirm_unsaved_projects = lambda *_args, **_kwargs: True
    try:
        host.show()
        app.processEvents()
        for index, canvas in ((0, host.studio.canvas), (1, host.wizard.canvas)):
            host.tabs.setCurrentIndex(index)
            app.processEvents()
            assert canvas.toolTip() == ''
            pos = QPoint(10, 10)
            ev = QHelpEvent(QEvent.Type.ToolTip, pos, canvas.mapToGlobal(pos))
            ev.ignore()
            app.sendEvent(canvas, ev)
            app.processEvents()
            assert ev.isAccepted(), 'The idle canvas ToolTip was not blocked'
            assert not QToolTip.isVisible()
        # The app must not strip ordinary help or optional Buddy speech.
        assert 'Slimer' in host.wizard.slimer_edit_asset.toolTip() or host.wizard.slimer_edit_asset.toolTip()
        assert host.studio.external_save_button.toolTip()
        assert host.wizard.buddy_bubble.text()
    finally:
        host.studio._dirty = False
        host.wizard.confirm_unsaved_projects = lambda *_args, **_kwargs: True
        host.close()
