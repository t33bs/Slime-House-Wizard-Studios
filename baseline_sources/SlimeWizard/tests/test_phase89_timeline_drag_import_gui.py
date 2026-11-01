"""Windows GUI regression for Import Pose PNG followed by timeline drag reorder.

The real Qt view changes its visual item order before the model rowMove callback.
Never interpret Qt's new currentRow as an old saved pose index, and never
refresh/repopulate a QListWidget inside its own dropEvent callback.
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
pytestmark = pytest.mark.usefixtures('isolate_gui_recovery')
pytest.importorskip('PySide6')
from PIL import Image
from PySide6.QtCore import QModelIndex
from PySide6.QtWidgets import QApplication, QFileDialog
from friendly_animator import Suite, PoseTimelineList


def test_import_new_pose_then_drag_reorder_preserves_both_sources_and_timings(tmp_path, monkeypatch):
    app = QApplication.instance() or QApplication([])
    w = Suite()
    w.confirm_unsaved_projects = lambda *a, **k: True
    w.show(); app.processEvents()
    try:
        assert isinstance(w.timeline, PoseTimelineList)
        animation = w.anim.currentText()
        first = Image.new('RGBA', (128, 128))
        first.putpixel((10, 10), (255, 20, 30, 255))
        w.model.import_part('First source', first)
        w.assets.addItem('First source')
        w.assets.setCurrentRow(0)
        w.model.insert_frame(animation, 0)
        w.select_timeline_pose(0)
        w.model.set_frame_duration(animation, 0, 125)
        original_p1 = w.model.render(w.model.animations[animation][0]).tobytes()
        original_source_png = w.model.animations[animation][0][0]['source_png']
        imported = Image.new('RGBA', (128, 128))
        imported.putpixel((70, 40), (90, 150, 235, 140))
        file_path = tmp_path / 'Swordcat_Walk_Pose_1_128.png'
        imported.save(file_path)
        monkeypatch.setattr(QFileDialog, 'getOpenFileName', lambda *a, **k: (str(file_path), 'PNG images (*.png)'))
        w.import_pose_png()
        assert len(w.model.animations[animation]) == 2
        # New PNG must not be written back into the old pose while switching.
        assert w.model.render(w.model.animations[animation][0]).tobytes() == original_p1
        assert w.model.animations[animation][0][0]['source_png'] == original_source_png
        assert len(w.model.animations[animation][0]) == 1
        assert len(w.model.animations[animation][1]) == 2
        w.model.set_frame_duration(animation, 1, 225)
        ids = list(w.model.pose_ids[animation])
        p1 = w.model.render(w.model.animations[animation][0]).tobytes()
        p2 = w.model.render(w.model.animations[animation][1]).tobytes()
        assert p1 != p2
        assert w.model.render().tobytes() == p2
        # User now selects Pose 1 to drag it to the second position.
        w.select_timeline_pose(0)
        # Edit first pose without explicitly calling mark_pose_draft: the drag
        # must detect and preserve the actual current snapshot before reorder.
        w.model.parts[0]['x'] = 2
        edited_p1 = w.model.render().tobytes()
        assert edited_p1 != p1
        # Mirror Qt's visual reorder event. QListWidget emits rowsMoved *in*
        # dropEvent, while its currentRowChanged is blocked by PoseTimelineList.
        w.timeline.blockSignals(True)
        try:
            w.timeline.setCurrentRow(1)  # transient visual selection
        finally:
            w.timeline.blockSignals(False)
        assert w.frame == 0  # no premature load of another pose
        w._timeline_rows_moved(QModelIndex(), 0, 0, QModelIndex(), 2)
        # Qt drop has completed; the queued model commit now runs.
        app.processEvents()
        assert w.model.pose_ids[animation] == ids[::-1]
        assert [w.model.frame_duration(animation, i) for i in range(2)] == [225, 125]
        assert w.model.render(w.model.animations[animation][0]).tobytes() == p2
        assert w.model.render(w.model.animations[animation][1]).tobytes() == edited_p1
        assert w.frame == 1
        assert w.model.render().tobytes() == edited_p1
        w.select_timeline_pose(0)
        assert w.model.render().tobytes() == p2
        w.select_timeline_pose(1)
        assert w.model.render().tobytes() == edited_p1
        w.undo()
        assert w.model.pose_ids[animation] == ids
        assert [w.model.frame_duration(animation, i) for i in range(2)] == [125, 225]
    finally:
        w.close()
