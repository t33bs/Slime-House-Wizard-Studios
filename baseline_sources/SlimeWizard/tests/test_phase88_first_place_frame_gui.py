"""Windows GUI gate: Pose 1 and every future pose use one editable Slimer base."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
pytestmark = pytest.mark.usefixtures('isolate_gui_recovery')
pytest.importorskip('PySide6')
from PIL import Image
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def test_first_place_frame_merges_edited_source_and_allows_reediting():
    app = QApplication.instance() or QApplication([])
    w = Suite()
    w.confirm_unsaved_projects = lambda *a, **k: True
    w.show()
    app.processEvents()
    try:
        image = Image.new('RGBA', (128, 128))
        image.putpixel((20, 30), (220, 80, 50, 255))
        image.putpixel((50, 60), (40, 200, 130, 138))
        w.model.import_part('Swordcat Source', image)
        w.assets.addItem('Swordcat Source')
        w.assets.setCurrentRow(0)
        w.slimer_toggle.setChecked(True)
        w.slimer_paint(20, 30, False)
        assert w.slimer_create_editable_layer(), w.status.text()
        w._slimer_pending_part['x'] = 4
        assert w.slimer_apply_move_to_pose(), w.status.text()
        old_art = w.model.render().tobytes()
        old_layer = w.model.snapshot()
        assert not w.model.animations.get(w.anim.currentText(), [])
        # This is the FIRST saved pose, not Pose 2.
        assert w.slimer_place_frame(), w.status.text()
        assert len(w.model.animations[w.anim.currentText()]) == 1
        assert w.frame == 0
        pose1 = w.model.animations[w.anim.currentText()][0]
        visible = [i for i,p in enumerate(pose1) if p.get('visible', True)]
        assert visible == [2], visible
        assert all(pose1[i]['source_png'] == old_layer[i]['source_png'] for i in range(2))
        assert w.model.render().tobytes() == old_art
        assert [i for i in range(w.assets.count()) if not w.assets.item(i).isHidden()] == [2]
        w.slimer_paint(50, 60, False)
        assert w.slimer_create_editable_layer(), w.status.text()
        w._slimer_pending_part['x'] = 3
        assert w.slimer_apply_move_to_pose(), w.status.text()
        assert w.slimer_place_frame(), w.status.text()
        assert len(w.model.animations[w.anim.currentText()]) == 2
        pose1_saved = w.model.animations[w.anim.currentText()][0]
        pose2_saved = w.model.animations[w.anim.currentText()][1]
        # Save-as-next: Pose 1 keeps the first move and its original
        # translucent pixel; Pose 2 contains the SECOND move only.
        assert [i for i, p in enumerate(pose1_saved) if p['visible']] == [2]
        assert [i for i, p in enumerate(pose2_saved) if p['visible']] == [4]
        w.select_timeline_pose(0)
        assert w.model.render().getpixel((50,60))[3] == 138
        assert w.model.render().getpixel((53,60))[3] == 0
        assert [i for i in range(w.assets.count()) if not w.assets.item(i).isHidden()] == [2]
        w.select_timeline_pose(1)
        assert w.model.render().getpixel((50,60))[3] == 0
        assert w.model.render().getpixel((53,60))[3] == 138
        assert [i for i in range(w.assets.count()) if not w.assets.item(i).isHidden()] == [4]
    finally:
        w.close()
