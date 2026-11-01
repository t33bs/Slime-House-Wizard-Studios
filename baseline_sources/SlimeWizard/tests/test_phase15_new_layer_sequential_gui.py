"""Regression for the actual Edit Selection workflow, not the legacy overlay."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest
from PIL import Image
pytest.importorskip("PySide6")
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


@pytest.mark.parametrize("move_original", [True, False])
def test_two_staged_layers_keep_independent_identity(move_original):
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *args, **kwargs: True
    try:
        source = Image.new("RGBA", (128, 128))
        source.putpixel((5, 5), (255, 0, 0, 255))
        source.putpixel((12, 12), (0, 0, 255, 255))
        window.model.import_part("source", source)
        window.assets.addItem("source")
        window.slimer_toggle.setChecked(True)
        window.slimer_move_original.setChecked(move_original)
        initial_frames = len(window.model.animations.get(window.anim.currentText(), []))
        identities = []
        for x, y in ((5, 5), (12, 12)):
            window.slimer_paint(x, y, False)
            assert window.slimer_create_editable_layer(), window.status.text()
            staged = window._slimer_pending_part
            assert staged is window.model.parts[-1]
            identities.append(staged)
            assert window.slimer_apply_move_to_pose(), window.status.text()
            assert window._slimer_pending_part is None
            assert not window.canvas.slimer_transform_mode
        assert identities[0] is not identities[1]
        assert all(any(p is item for p in window.model.parts) for item in identities)
        assert len(window.model.animations.get(window.anim.currentText(), [])) == initial_frames
        assert window.model.render().getpixel((5, 5))[3] > 0
        assert window.model.render().getpixel((12, 12))[3] > 0
    finally:
        window.close()


def test_missing_staged_layer_can_be_cancelled_without_stranding_controls():
    app = QApplication.instance() or QApplication([])
    window = Suite()
    window.confirm_unsaved_projects = lambda *args, **kwargs: True
    try:
        image = Image.new("RGBA", (128, 128))
        image.putpixel((8, 8), (255, 0, 0, 255))
        window.model.import_part("source", image)
        window.assets.addItem("source")
        window.slimer_toggle.setChecked(True)
        window.slimer_paint(8, 8, False)
        assert window.slimer_create_editable_layer()
        pending = window._slimer_pending_part
        idx = next(i for i, part in enumerate(window.model.parts) if part is pending)
        # Simulate external loss of the provisional layer using the model's
        # safe removal API.  Unrotated layers have no angles[index] entry.
        window.model.remove_unconfirmed_part(idx)
        window.assets.takeItem(idx)
        assert window.slimer_cancel_editable_layer() is False
        assert window._slimer_pending_part is None
        assert window.slimer_move_original.isEnabled()
        assert window.model.render().getpixel((8, 8))[3] > 0
    finally:
        window.close()
