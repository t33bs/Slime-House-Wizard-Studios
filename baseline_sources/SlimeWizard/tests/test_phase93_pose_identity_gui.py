"""Phase 93 Windows GUI acceptance: editing Pose 2 never rewrites Pose 1.

The primary test deliberately creates visually *different* poses before placing
Pose 3. This catches the reported regression missed by a test that only
compared two copies of the same pose.  No autosave dialogs or user files used.
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytestmark = pytest.mark.usefixtures('isolate_gui_recovery')
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def _window():
    app = QApplication.instance() or QApplication([])
    w = Suite()
    w.confirm_unsaved_projects = lambda *a, **k: True
    w.show()
    app.processEvents()
    return w


def _paint_and_move(w, xy, dx):
    w.slimer_paint(*xy, False)
    assert w.slimer_create_editable_layer(), w.status.text()
    w._slimer_pending_part['x'] = dx
    assert w.slimer_apply_move_to_pose(), w.status.text()


def test_three_poses_keep_distinct_pixels_and_asset_layers_after_next_place():
    w = _window()
    try:
        source = Image.new('RGBA', (128,128))
        source.putpixel((18,25), (255,0,0,255))
        source.putpixel((52,63), (0,175,220,255))
        source.putpixel((96,105), (33,27,21,255))
        w.model.import_part('Swordcat body', source)
        w.assets.addItem('Swordcat body')
        w.assets.setCurrentRow(0)
        w.slimer_toggle.setChecked(True)
        animation = w.anim.currentText()
        assert w.slimer_place_frame(), w.status.text()
        initial = w.model.render(w.model.animations[animation][0]).tobytes()
        first_id = w.model.pose_id(animation, 0)
        # The user's first post-Place edits must create a DIFFERENT Pose 2.
        _paint_and_move(w, (18,25), 4)
        assert w.slimer_place_frame(), w.status.text()
        assert len(w.model.animations[animation]) == 2
        second_id = w.model.pose_id(animation, 1)
        pose1 = w.model.animations[animation][0]
        pose2 = w.model.animations[animation][1]
        before1 = w.model.render(pose1).tobytes()
        before2 = w.model.render(pose2).tobytes()
        assert before1 == initial
        assert before1 != before2
        assert w.model.render(pose1).getpixel((18,25)) == (255,0,0,255)
        assert w.model.render(pose2).getpixel((22,25)) == (255,0,0,255)
        assert [i for i,p in enumerate(pose1) if p['visible']] == [0]
        assert len([i for i,p in enumerate(pose2) if p['visible']]) == 1

        # A different edit is captured as Pose 3 WITHOUT rewriting Pose 2.
        _paint_and_move(w, (52,63), 5)
        assert w.slimer_place_frame(), w.status.text()
        assert len(w.model.animations[animation]) == 3
        pose3 = w.model.animations[animation][2]
        assert w.model.render(pose1).tobytes() == before1
        assert w.model.render(pose2).tobytes() == before2
        assert w.model.render(pose3).getpixel((57,63)) == (0,175,220,255)
        assert w.model.render(pose3).getpixel((22,25)) == (255,0,0,255)
        assert w.model.pose_ids[animation][:2] == [first_id, second_id]
        w.select_timeline_pose(0)
        assert w.model.render().tobytes() == before1
        w.select_timeline_pose(1)
        assert w.model.render().tobytes() == before2
        w.select_timeline_pose(2)
        assert w.model.render().tobytes() != before2
        w.select_timeline_pose(0)
        assert w.model.render().tobytes() == before1
    finally:
        w.close()


def test_stale_canvas_identity_cannot_auto_save_into_another_pose():
    w = _window()
    try:
        source = Image.new('RGBA', (128,128), (0,0,0,0))
        source.putpixel((5,7), (255,70,30,255))
        w.model.import_part('cat', source)
        w.assets.addItem('cat')
        animation = w.anim.currentText()
        w.model.insert_frame(animation, 0)
        w.model.insert_frame(animation, 1)
        w.select_timeline_pose(0)
        pose1_id = w.model.pose_id(animation, 0)
        pose1_saved = w.model.render(w.model.animations[animation][0]).tobytes()
        w.select_timeline_pose(1)
        pose2_id = w.model.pose_id(animation, 1)
        # Emulate a stale widget draft index after a timeline edit. Live canvas
        # belongs to Pose 2 but an old callback still thinks it owns Pose 1.
        w._pose_draft_key = (w._active_project_id, animation, 0, pose1_id)
        assert w._pose_live_id == pose2_id
        w.model.parts[0]['x'] = 8
        w.preserve_pose_draft()
        assert w.model.render(w.model.animations[animation][0]).tobytes() == pose1_saved
        assert 'not auto-saved' in w.status.text()
        # Explicit Save Current Pose must also fail closed.
        w.frame = 0
        w.save_frame()
        assert w.model.render(w.model.animations[animation][0]).tobytes() == pose1_saved
        assert 'Cannot save this pose' in w.status.text()
        # The Place Frame action also fails closed against stale widget rows.
        old_ids = list(w.model.pose_ids[animation])
        assert w.slimer_place_frame() is False
        assert w.model.pose_ids[animation] == old_ids
        assert w.model.render(w.model.animations[animation][0]).tobytes() == pose1_saved
    finally:
        w.close()
