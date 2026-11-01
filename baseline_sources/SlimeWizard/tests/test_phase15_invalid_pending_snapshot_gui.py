"""Regression: invalid staged source metadata must fail closed, not crash/erase."""
import os
import pytest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
pytest.importorskip('PySide6')

from PIL import Image
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_apply_move_rejects_missing_source_snapshot():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    try:
        # The check is deliberately exercised without requiring an imported
        # artwork file or an active GUI selection.
        sentinel = {'name': 'provisional'}
        window._slimer_pending_part = sentinel
        window._slimer_pending_layer = 0
        window._slimer_pending_source = None
        window._slimer_pending_mask = Image.new('L', window.model.size, 255)
        window._slimer_pending_move_original = True
        before = window.model.render().tobytes()
        assert window.slimer_apply_move_to_pose() is False
        assert window.model.render().tobytes() == before
        assert 'snapshot' in window.status.text().lower()
    finally:
        window.close()
