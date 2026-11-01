"""Apply Move succeeds only after Edit Selection stages a real editable layer."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytestmark = pytest.mark.usefixtures('isolate_gui_recovery')
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_apply_move_reports_failure_then_success_and_does_not_create_frame():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *a, **kw: True
    try:
        image = Image.new('RGBA', (128, 128))
        color = (255, 80, 10, 180)  # isolated translucent source stays RGBA-exact
        image.putpixel((4, 4), color)
        window.model.import_part('source', image)
        window.assets.addItem('source')
        window.slimer_toggle.setChecked(True)
        window.slimer_move_original.setChecked(True)
        animation = window.anim.currentText()
        initial_frames = len(window.model.animations.get(animation, []))

        assert window.slimer_apply_move_to_pose() is False  # no highlighted pixels
        window.slimer_paint(4, 4, False)
        assert window.slimer_apply_move_to_pose() is False  # highlight isn't a layer
        assert window.slimer_create_editable_layer(), window.status.text()
        assert window._slimer_pending_part is window.model.parts[-1]
        window.x.setValue(2)  # live asset table, not the obsolete float-preview dx
        assert window.model.parts[-1]['x'] == 2
        assert window.slimer_apply_move_to_pose() is True, window.status.text()
        assert window.model.render().getpixel((4, 4))[3] == 0
        assert window.model.render().getpixel((6, 4)) == color
        assert len(window.model.animations.get(animation, [])) == initial_frames
        assert window._slimer_pending_part is None
        assert window.slimer_apply_move_to_pose() is False  # completed selection cleared
    finally:
        window.close()
