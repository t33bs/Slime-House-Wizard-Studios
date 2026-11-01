"""Windows/Qt regression: three real Edit Selection -> table move -> Apply Move cycles."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
from PIL import Image
pytest.importorskip("PySide6")
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_three_consecutive_moves_through_asset_edit_table():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *a, **k: True
    try:
        source = Image.new("RGBA", (128, 128))
        source.putpixel((8, 8), (240, 40, 20, 255))
        source.putpixel((24, 8), (20, 80, 240, 255))
        window.model.import_part("source", source)
        window.assets.addItem("source")
        window.slimer_toggle.setChecked(True)
        window.slimer_move_original.setChecked(True)
        frame_count = len(window.model.animations.get(window.anim.currentText(), []))
        for x, destination in ((8, 40), (24, 56), (40, 72)):
            window.slimer_paint(x, 8, False)
            assert window.slimer_create_editable_layer(), window.status.text()
            pending = window._slimer_pending_part
            assert pending is window.model.parts[-1]
            index = len(window.model.parts) - 1
            window.assets.setCurrentRow(index)
            window.select_asset(index)
            window.x.setValue(destination - x)
            # QSpinBox.valueChanged must invoke the production editing slot.
            # Calling update_asset() manually here would mask a broken GUI connection.
            assert window.model.parts[index]["x"] == destination - x
            assert window.slimer_apply_move_to_pose(), window.status.text()
            assert window._slimer_pending_part is None
            assert window.model.render().getpixel((x, 8))[3] == 0
            assert window.model.render().getpixel((destination, 8))[3] == 255
        assert len(window.model.animations.get(window.anim.currentText(), [])) == frame_count
        assert len(window.model.parts) == 4
    finally:
        window.close()
