"""Windows UI acceptance: long sequence of Cleaner edits, timeline switching, Undo."""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
from shws_wizard.friendly_animator import Suite


def test_cleaner_stroke_does_not_lock_canvas_to_one_pose_and_undo_resets_state():
    app=QApplication.instance() or QApplication([])
    w=Suite()
    w.confirm_unsaved_projects=lambda *_a,**_kw:True
    w.show();app.processEvents()
    try:
        image=Image.new('RGBA',(128,128))
        image.putpixel((20,30),(210,30,70,255))
        w.model.import_part('Test sprite',image)
        w.assets.addItem('Test sprite')
        name=w.anim.currentText()
        for j in range(12):
            w.model.parts[0]['x']=j*3
            w.model.save_frame(name)
        w.select_timeline_pose(6)
        before=[w.model.render(p).tobytes() for p in w.model.animations[name]]
        w.cleaner_toggle.setChecked(True)
        # A normal Cleaner stroke must NOT become an unplaced next pose.
        w.canvas.cleaner_stroke_start.emit()
        w.canvas.cleaner_stroke.emit(20+6*3,30)
        w.canvas.cleaner_stroke_end.emit()
        assert not w._next_pose_capture_pending
        w.select_timeline_pose(2)
        assert w.frame==2 and w._pose_live_id==w.model.pose_id(name,2)
        assert w.model.render().tobytes()==before[2]
        after=[w.model.render(p).tobytes() for p in w.model.animations[name]]
        assert len(set(after))==12
        for i in range(30):
            index=i%12
            w.select_timeline_pose(index)
            assert w.model.render().tobytes()==w.model.render(w.model.animations[name][index]).tobytes()
        w.undo()
        for i in range(12):
            w.select_timeline_pose(i)
            assert w.model.render().tobytes()==w.model.render(w.model.animations[name][i]).tobytes()
    finally:
        w.close()
