"""Phase 87 Windows GUI gate: new pose gets a single Slimer-ready merged base.

Every prior pose retains its individual layers. A third pose remerges from
whatever is visible after editing Pose 2; Apply Move never creates a frame.
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest
pytestmark=pytest.mark.usefixtures('isolate_gui_recovery')
pytest.importorskip('PySide6')
from PIL import Image
from PySide6.QtWidgets import QApplication
from friendly_animator import Suite


def make_window():
    app=QApplication.instance() or QApplication([])
    w=Suite()
    w.confirm_unsaved_projects=lambda *args,**kwargs: True
    w.resize(1400,900)
    w.show()
    app.processEvents()
    return w


def test_two_layer_moves_merge_in_next_pose_and_reedit_again():
    w=make_window()
    try:
        source=Image.new('RGBA',(128,128))
        for xy,rgba in {
            (25,60):(200,85,60,255),
            (26,60):(150,90,45,255),
            (70,80):(80,210,100,132),
            (71,80):(60,180,85,255),
            (90,90):(180,80,200,255),
        }.items():source.putpixel(xy,rgba)
        w.model.import_part('Swordcat Source',source)
        w.assets.addItem('Swordcat Source')
        w.assets.setCurrentRow(0)
        animation=w.anim.currentText()
        w.model.insert_frame(animation,0)
        w.select_timeline_pose(0)
        w.slimer_toggle.setChecked(True)
        # The live canvas accumulates TWO Slimer edits. The already saved
        # Pose 1 must remain its original single source layer.
        w.slimer_paint(25,60,False)
        assert w.slimer_create_editable_layer(),w.status.text()
        w._slimer_pending_part['x']=3
        assert w.slimer_apply_move_to_pose(),w.status.text()
        w.slimer_paint(70,80,False)
        w.slimer_paint(71,80,False)
        assert w.slimer_create_editable_layer(),w.status.text()
        w._slimer_pending_part['x']=4
        assert w.slimer_apply_move_to_pose(),w.status.text()
        assert len(w.model.parts)==3
        assert len(w.model.animations[animation])==1
        pose1_render=w.model.render(w.model.animations[animation][0]).tobytes()
        two_move_art=w.model.render().tobytes()
        assert pose1_render != two_move_art
        assert w.slimer_place_frame(),w.status.text()
        assert len(w.model.animations[animation])==2
        assert w.frame==1
        assert len(w.model.parts)==4
        # Phase 96 captures the edits AS NEW Pose 2. Pose 1's previously
        # saved source stays pristine, rather than inheriting edit layers.
        assert len(w.model.animations[animation][0]) == 1
        assert w.model.animations[animation][0][0]['name'] == 'Swordcat Source'
        new=w.model.animations[animation][1]
        assert [i for i,s in enumerate(new) if s['visible']]==[3]
        assert w.model.render(new).tobytes()==two_move_art
        assert w.model.render(w.model.animations[animation][0]).tobytes()==pose1_render
        assert w.assets.currentRow()==3
        assert [i for i in range(w.assets.count()) if not w.assets.item(i).isHidden()]==[3]
        assert w.canvas.slimer_active
        # Slimer must treat the new combined layer as ordinary editable pixels.
        assert w.slimer_selection.mask.getbbox() is None
        w.slimer_paint(90,90,False)
        assert w.slimer_create_editable_layer(),w.status.text()
        w._slimer_pending_part['x']=-5
        assert w.slimer_apply_move_to_pose(),w.status.text()
        assert len(w.model.animations[animation])==2
        assert w.model.render().getpixel((90,90))[3]==0
        assert w.model.render().getpixel((85,90))==(180,80,200,255)
        assert w.slimer_place_frame(),w.status.text()
        assert len(w.model.animations[animation])==3
        assert len([s for s in w.model.animations[animation][2] if s['visible']])==1
        assert w.model.render().getpixel((85,90))==(180,80,200,255)
        # Returning to Pose 1 restores its untouched original artwork.
        w.select_timeline_pose(0)
        assert w.model.render().tobytes()==pose1_render
        assert [i for i in range(3) if not w.assets.item(i).isHidden()]==[0]
        # Pose 2 keeps its two original moves, but NOT the third edit
        # that was captured into new Pose 3.
        w.select_timeline_pose(1)
        assert w.model.render().getpixel((90,90))==(180,80,200,255)
        assert w.model.render().getpixel((85,90))[3]==0
        assert [i for i,s in enumerate(w.model.animations[animation][1]) if s['visible']]==[3]
        w.select_timeline_pose(2)
        assert w.model.render().getpixel((85,90))==(180,80,200,255)
    finally:
        w.close()


def test_regular_rig_pose_insertion_keeps_separate_assets():
    w=make_window()
    try:
        a=Image.new('RGBA',(128,128));a.putpixel((4,5),(70,30,200,255))
        b=Image.new('RGBA',(128,128));b.putpixel((6,7),(30,100,150,220))
        for name,source in [('Body',a),('Hat',b)]:
            w.model.import_part(name,source)
            w.assets.addItem(name)
        w.assets.setCurrentRow(0)
        w.model.insert_frame(w.anim.currentText(),0)
        w.select_timeline_pose(0)
        w.duplicate_frame()
        assert len(w.model.parts)==2
        assert len(w.model.animations[w.anim.currentText()])==2
        assert len([p for p in w.model.parts if p['visible']])==2
    finally:
        w.close()
