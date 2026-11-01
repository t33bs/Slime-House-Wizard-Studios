"""Phase 76: selected Asset Library layer gets three independent X/Y/R controls.

Run on Windows with the existing PySide6 environment (offscreen is fine for CI).
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtCore import Qt, QPoint
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def _source():
    pic=Image.new('RGBA',(128,128))
    for x,y,color in ((42,50,(244,80,40,255)),(43,50,(60,190,40,255)),
                      (42,51,(20,70,230,255))):
        pic.putpixel((x,y),color)
    return pic


def _window():
    app=QApplication.instance() or QApplication([])
    window=Suite()
    window.confirm_unsaved_projects=lambda *a,**kw: True
    window.resize(1450,950)
    window.show()
    app.processEvents()
    window.model.import_part('source',_source())
    window.assets.addItem('source')
    window.assets.setCurrentRow(0)
    window.slimer_toggle.setChecked(True)
    for p in ((42,50),(43,50),(42,51)):
        window.slimer_paint(*p,False)
    window.slimer_edit_asset.click()
    assert window._slimer_pending_part is not None,window.status.text()
    assert window.canvas.asset_controls_enabled
    return app,window


def _screen(canvas, xy):
    scale,ox,oy=canvas._geometry()
    return QPoint(round(ox+xy[0]*scale),round(oy+xy[1]*scale))


def _drag(app, canvas, before, after):
    QTest.mousePress(canvas,Qt.MouseButton.LeftButton,pos=_screen(canvas,before))
    QTest.mouseMove(canvas,pos=_screen(canvas,after))
    QTest.mouseRelease(canvas,Qt.MouseButton.LeftButton,pos=_screen(canvas,after))
    app.processEvents()


def test_staged_controls_x_and_y_are_independent_and_rotate_in_degrees():
    app,w=_window()
    try:
        original=w.model.parts[0]['image'].tobytes()
        selected=w.selected
        assert 'Slimer Layer' in w.active_asset_label.text()
        assert 'Handles ON' in w.active_asset_label.text()
        assert w.assets.currentRow()==selected
        corners,handles,pivot=w.canvas._asset_transform_geometry(selected)
        assert set(handles)=={'move_x','move_y','rotate','resize'}
        for action,where in handles.items():
            w.canvas.set_canvas_handle_mode(action)
            assert w.canvas._asset_transform_hit(_screen(w.canvas,where))==action
        w.canvas.set_canvas_handle_mode('move_x')
        initial_x=w.model.parts[selected]['x']
        initial_y=w.model.parts[selected]['y']
        _drag(app,w.canvas,handles['move_x'],(handles['move_x'][0]+9,handles['move_x'][1]+12))
        assert w.model.parts[selected]['x']==initial_x+9
        assert w.model.parts[selected]['y']==initial_y
        handles=w.canvas._asset_transform_geometry(selected)[1]
        w.canvas.set_canvas_handle_mode('move_y')
        _drag(app,w.canvas,handles['move_y'],(handles['move_y'][0]+12,handles['move_y'][1]+6))
        assert w.model.parts[selected]['x']==initial_x+9
        assert w.model.parts[selected]['y']==initial_y+6
        pivot,handle,_=w.canvas._selected_rotation_geometry(selected)
        w.canvas.set_canvas_handle_mode('rotate')
        _drag(app,w.canvas,handle,(pivot[0]+14,pivot[1]))
        assert w.model.angles[selected]==90
        assert w.angle.value()==90
        assert w.model.parts[0]['image'].tobytes()==original
        assert w._slimer_pending_part is w.model.parts[selected]
        assert w.slimer_apply_move_to_pose(),w.status.text()
        assert w.model.parts[0]['image'].getpixel((42,50))[3]==0
    finally:
        w.close()


def test_edit_selection_toggles_handles_without_recreating_asset():
    app,w=_window()
    try:
        selected=w.selected
        old_count=len(w.model.parts)
        source_bytes=w.model.parts[0]['image'].tobytes()
        w.slimer_edit_asset.click()
        assert not w.canvas.asset_controls_enabled
        assert w.canvas._asset_transform_hit(_screen(w.canvas,w.canvas._asset_transform_geometry(selected)[1]['rotate'])) is None
        assert 'Handles OFF' in w.active_asset_label.text()
        w.slimer_edit_asset.click()
        assert w.canvas.asset_controls_enabled
        assert len(w.model.parts)==old_count
        assert w._slimer_pending_part is w.model.parts[selected]
        assert w.model.parts[0]['image'].tobytes()==source_bytes
    finally:
        w.close()


def test_library_selection_controls_correct_asset_and_pending_lock():
    app,w=_window()
    try:
        selected=w.selected
        # A source change before Apply would make the erase snapshot stale.
        w.assets.setCurrentRow(0)
        assert w.assets.currentRow()==selected
        assert w.selected==selected
        assert 'Apply Move or Cancel' in w.status.text()
        assert w.slimer_apply_move_to_pose(),w.status.text()
        # Move Original erased the only opaque source pixels, so selecting
        # source and pressing Edit Selection should NOT turn a blank asset
        # into a new editable layer.  Choose the confirmed visible layer
        # first; its handles can then follow ordinary library selection.
        assert w.model.parts[0]['image'].getchannel('A').getbbox() is None
        w.assets.setCurrentRow(1)
        count=len(w.model.parts)
        w.slimer_edit_asset.click()
        assert w.canvas.asset_controls_enabled
        assert len(w.model.parts)==count
        assert 'Slimer Layer' in w.active_asset_label.text()
        w.assets.setCurrentRow(0)
        assert w.selected==0
        assert 'source' in w.active_asset_label.text()
        w.assets.setCurrentRow(1)
        assert w.selected==1
        assert 'Slimer Layer' in w.active_asset_label.text()
        assert len(w.model.parts)==count
    finally:
        w.close()


def test_cancel_hidden_handles_preserves_source_and_no_pose_creation():
    app,w=_window()
    try:
        source=w.model.parts[0]['image'].tobytes()
        poses=len(w.model.animations.get(w.anim.currentText(),[]))
        w.slimer_edit_asset.click() # hide controls
        assert w.slimer_cancel_editable_layer(),w.status.text()
        assert not w.canvas.asset_controls_enabled
        assert w.model.parts[0]['image'].tobytes()==source
        assert len(w.model.parts)==1
        assert len(w.model.animations.get(w.anim.currentText(),[]))==poses
    finally:
        w.close()
