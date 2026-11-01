"""Real widget click regression for the reported Pose 2 overwrites Pose 1 bug.

Tests use clickable Place Frame / Edit Selection / Apply Move controls and the
Qt timeline selection signal, not only direct Suite method calls.  They use
visibly different poses, original colors/alpha, and a project save-reopen.
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

import pytest
from PIL import Image

pytestmark = pytest.mark.usefixtures('isolate_gui_recovery')
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication, QPushButton
from friendly_animator import Suite
from studio.pet_suite_model import PetSuiteModel


def test_real_buttons_place_three_poses_preserves_pose_one_and_pose_two(tmp_path):
    app = QApplication.instance() or QApplication([])
    w = Suite()
    w.confirm_unsaved_projects = lambda *a, **k: True
    w.show()
    app.processEvents()
    try:
        source = Image.new('RGBA', (128,128))
        source.putpixel((12,23), (17,25,31,255))
        source.putpixel((62,73), (244,38,110,255))
        source.putpixel((85,91), (100,200,80,151))
        w.model.import_part('Walking Swordcat', source)
        w.assets.addItem('Walking Swordcat')
        w.assets.setCurrentRow(0)
        w.slimer_toggle.setChecked(True)
        animation = w.anim.currentText()
        frame_button = w.slimer_place_frame_button
        assert isinstance(frame_button, QPushButton)
        frame_button.click()
        assert len(w.model.animations[animation]) == 1, w.status.text()
        pose1 = w.model.render(w.model.animations[animation][0]).tobytes()
        pid1 = w.model.pose_id(animation, 0)

        # Two later edits must not write to the SAVED previous frame.
        w.slimer_paint(12, 23, False)
        w.slimer_edit_asset.click()
        assert w._slimer_pending_part is not None, w.status.text()
        w._slimer_pending_part['x'] = 4
        w.slimer_apply_move.click()
        assert w._slimer_pending_part is None, w.status.text()
        frame_button.click()
        assert len(w.model.animations[animation]) == 2, w.status.text()
        assert w.model.render(w.model.animations[animation][0]).tobytes() == pose1
        assert w.model.pose_id(animation, 0) == pid1
        pose2 = w.model.render(w.model.animations[animation][1]).tobytes()
        assert pose1 != pose2
        assert w.model.render(w.model.animations[animation][1]).getpixel((16,23)) == (17,25,31,255)

        w.slimer_paint(62,73,False)
        w.slimer_edit_asset.click()
        assert w._slimer_pending_part is not None, w.status.text()
        w._slimer_pending_part['x'] = 7
        w.slimer_apply_move.click()
        assert w._slimer_pending_part is None, w.status.text()
        frame_button.click()
        assert len(w.model.animations[animation]) == 3, w.status.text()
        pose3 = w.model.render(w.model.animations[animation][2]).tobytes()
        assert pose3 != pose2
        assert w.model.render(w.model.animations[animation][2]).getpixel((69,73)) == (244,38,110,255)
        assert w.model.render(w.model.animations[animation][1]).tobytes() == pose2
        assert w.model.render(w.model.animations[animation][0]).tobytes() == pose1

        w.timeline.setCurrentRow(0)
        app.processEvents()
        assert w.model.render().tobytes() == pose1
        w.timeline.setCurrentRow(1)
        app.processEvents()
        assert w.model.render().tobytes() == pose2
        w.timeline.setCurrentRow(2)
        app.processEvents()
        assert w.model.render().tobytes() == pose3
        w.timeline.setCurrentRow(0)
        app.processEvents()
        assert w.model.render().tobytes() == pose1

        path = tmp_path / 'swordcat.rig.json'
        w.preserve_pose_draft()
        w.model.save_project(path)
        reopened = PetSuiteModel.load_project(path)
        assert reopened.render(reopened.animations[animation][0]).tobytes() == pose1
        assert reopened.render(reopened.animations[animation][1]).tobytes() == pose2
        assert reopened.render(reopened.animations[animation][2]).tobytes() == pose3
    finally:
        w.close()


def test_place_frame_reports_copy_then_does_not_change_prior_pose():
    app = QApplication.instance() or QApplication([])
    w = Suite()
    w.confirm_unsaved_projects = lambda *a, **k: True
    w.show()
    app.processEvents()
    try:
        art = Image.new('RGBA', (128, 128))
        art.putpixel((3, 5), (11, 22, 33, 255))
        w.model.import_part('Start', art)
        w.assets.addItem('Start')
        name = w.anim.currentText()
        w.slimer_place_frame_button.click()
        saved = w.model.render(w.model.animations[name][0]).tobytes()
        w.slimer_place_frame_button.click()
        assert w.model.render(w.model.animations[name][0]).tobytes() == saved
        assert 'older 1 pose(s) verified unchanged' in w.status.text()
        assert w.model.pose_id(name, 0) != w.model.pose_id(name, 1)
    finally:
        w.close()
