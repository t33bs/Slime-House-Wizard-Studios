"""Windows GUI acceptance for the precise reported beginner workflow.

Click Place Frame to capture the original, highlight/move two leg pixels with
Edit Selection -> Apply Move twice, then click Place Frame to capture *new*
artwork. The original saved thumbnail and source must remain unchanged.
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytestmark = pytest.mark.usefixtures('isolate_gui_recovery')
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite
from studio.pet_suite_model import PetSuiteModel


def _make_window():
    app = QApplication.instance() or QApplication([])
    w = Suite()
    w.confirm_unsaved_projects = lambda *args, **kwargs: True
    w.show()
    app.processEvents()
    return w


def _move_with_real_buttons(w, point, dx):
    w.slimer_paint(point[0], point[1], False)
    w.slimer_edit_asset.click()
    assert w._slimer_pending_part is not None, w.status.text()
    w._slimer_pending_part['x'] = dx
    w.slimer_apply_move.click()
    assert w._slimer_pending_part is None, w.status.text()


def test_two_leg_edits_capture_into_new_frame_not_previous_and_roundtrip(tmp_path):
    app = QApplication.instance() or QApplication([])
    w = _make_window()
    try:
        image = Image.new('RGBA', (128, 128))
        image.putpixel((20, 80), (200, 40, 50, 255))
        image.putpixel((60, 80), (30, 170, 250, 255))
        image.putpixel((90, 25), (120, 80, 60, 155))
        w.model.import_part('Swordcat', image)
        w.assets.addItem('Swordcat')
        w.assets.setCurrentRow(0)
        w.slimer_toggle.setChecked(True)
        animation = w.anim.currentText()

        # 1. User clicks Place Frame FIRST: this records their untouched base.
        w.slimer_place_frame_button.click()
        assert len(w.model.animations[animation]) == 1, w.status.text()
        original = w.model.render(w.model.animations[animation][0]).tobytes()
        original_layers = w.model.animations[animation][0]
        original_id = w.model.pose_id(animation, 0)

        # 2. User moves BOTH legs on the working canvas (not the saved source).
        _move_with_real_buttons(w, (20, 80), 4)
        _move_with_real_buttons(w, (60, 80), -5)
        assert w.model.render().tobytes() != original
        assert w.model.render().getpixel((24, 80)) == (200, 40, 50, 255)
        assert w.model.render().getpixel((55, 80)) == (30, 170, 250, 255)
        # Important: even before Place Frame the saved original is intact.
        assert w.model.render(w.model.animations[animation][0]).tobytes() == original

        # 3. Place Frame captures the changes AS Pose 2, not over Pose 1.
        w.slimer_place_frame_button.click()
        assert len(w.model.animations[animation]) == 2, w.status.text()
        assert w.model.pose_id(animation, 0) == original_id
        assert w.model.animations[animation][0] == original_layers
        assert w.model.render(w.model.animations[animation][0]).tobytes() == original
        changed = w.model.render(w.model.animations[animation][1]).tobytes()
        assert changed != original
        assert w.model.render(w.model.animations[animation][1]).getpixel((24, 80)) == (200, 40, 50, 255)
        assert w.model.render(w.model.animations[animation][1]).getpixel((55, 80)) == (30, 170, 250, 255)
        assert w.frame == w.timeline.currentRow() == 1
        assert 'older 1 pose(s) verified unchanged' in w.status.text()

        # 4. Switching actual GUI timeline rows shows two different art poses.
        w.timeline.setCurrentRow(0)
        app.processEvents()
        assert w.model.render().tobytes() == original
        w.timeline.setCurrentRow(1)
        app.processEvents()
        assert w.model.render().tobytes() == changed

        # 5. Saved project still has both distinct poses after reopening.
        path = tmp_path / 'walk.rig.json'
        w.preserve_pose_draft()
        w.model.save_project(path)
        reopened = PetSuiteModel.load_project(path)
        assert reopened.render(reopened.animations[animation][0]).tobytes() == original
        assert reopened.render(reopened.animations[animation][1]).tobytes() == changed
    finally:
        w.close()


def test_save_current_pose_is_explicit_way_to_replace_selected_frame():
    w = _make_window()
    try:
        source = Image.new('RGBA', (128, 128))
        source.putpixel((4, 10), (100, 200, 50, 255))
        w.model.import_part('Body', source)
        w.assets.addItem('Body')
        w.assets.setCurrentRow(0)
        w.slimer_place_frame_button.click()
        name = w.anim.currentText()
        old = w.model.render(w.model.animations[name][0]).tobytes()
        w.model.parts[0]['x'] = 2
        w.mark_pose_draft()
        assert w.model.render(w.model.animations[name][0]).tobytes() == old
        # User explicitly commits to the *same* pose instead of capturing next.
        w.save_frame()
        assert len(w.model.animations[name]) == 1
        assert w.model.render(w.model.animations[name][0]).tobytes() != old
        assert w.model.render(w.model.animations[name][0]).getpixel((6, 10)) == (100, 200, 50, 255)
    finally:
        w.close()
