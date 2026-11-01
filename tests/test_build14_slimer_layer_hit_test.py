"""Build 1.4: reselect the first confirmed Slimer layer after the second move."""
from PIL import Image
from shws_wizard.studio.asset_hit_test import choose_drag_layer
from shws_wizard.studio.pet_suite_model import PetSuiteModel


def make_model():
    model=PetSuiteModel((128,128))
    # Each moved selection is stored as a full-canvas transparent layer.
    image1=Image.new('RGBA',(128,128))
    image1.putpixel((12,12),(240,30,30,255))
    image2=Image.new('RGBA',(128,128))
    image2.putpixel((70,70),(40,40,230,255))
    model.import_part('Slimer Layer 001',image1)
    model.import_part('Slimer Layer 002',image2)
    return model


def exact_hit(model,index,x,y):
    if not 0<=x<model.size[0] or not 0<=y<model.size[1]:
        return False
    return model.render_part(index,model.resolved_pose()[index]).getpixel((x,y))[3]>0


def test_second_full_canvas_layer_does_not_steal_first_move():
    m=make_model()
    before=[part['image'].tobytes() for part in m.parts]
    assert choose_drag_layer(m.parts,0,12,12,lambda i,x,y:exact_hit(m,i,x,y))==0
    assert choose_drag_layer(m.parts,1,70,70,lambda i,x,y:exact_hit(m,i,x,y))==1
    assert choose_drag_layer(m.parts,0,50,50,lambda i,x,y:exact_hit(m,i,x,y)) is None
    # Hit test must be read-only (and must not re-enter Slimer staging).
    assert [p['image'].tobytes() for p in m.parts]==before


def test_selected_first_layer_wins_overlap_with_later_layer():
    m=make_model()
    m.parts[1]['x']=-58
    m.parts[1]['y']=-58
    hit=lambda i,x,y:exact_hit(m,i,x,y)
    assert hit(0,12,12) and hit(1,12,12)
    assert choose_drag_layer(m.parts,0,12,12,hit)==0
    assert choose_drag_layer(m.parts,1,12,12,hit)==1
    # No selection -> conventional last-visible (topmost) layer wins.
    assert choose_drag_layer(m.parts,-1,12,12,hit)==1


def test_pending_layer_is_locked_even_if_first_layer_is_selected():
    m=make_model()
    hit=lambda i,x,y:exact_hit(m,i,x,y)
    pending=m.parts[1]
    assert choose_drag_layer(m.parts,0,12,12,hit,staged=pending) is None
    assert choose_drag_layer(m.parts,0,70,70,hit,staged=pending)==1
    assert choose_drag_layer(m.parts,0,12,12,hit,staged=dict(pending)) is None


def test_hidden_or_off_canvas_and_fully_transparent_are_not_draggable():
    m=make_model()
    m.parts[0]['visible']=False
    hit=lambda i,x,y:exact_hit(m,i,x,y)
    assert choose_drag_layer(m.parts,0,12,12,hit) is None
    m.parts[0]['visible']=True
    m.parts[0]['x']=300
    assert choose_drag_layer(m.parts,0,12,12,hit) is None
    assert choose_drag_layer(m.parts,0,200,200,hit) is None


def test_rotated_alpha_hit_uses_actual_render_not_unrotated_rect():
    m=make_model()
    m.set_anchor(0,12,12)
    m.rotate_part(0,90)
    hit=lambda i,x,y:exact_hit(m,i,x,y)
    # Pillow's NEAREST rotation shifts the 1px sample by one pixel here.
    # Follow the same rendered alpha as the actual canvas; never an
    # approximate unrotated bounding box.
    bbox=m.render_part(0,m.resolved_pose()[0]).getchannel('A').getbbox()
    assert bbox is not None
    x,y=bbox[:2]
    assert choose_drag_layer(m.parts,0,x,y,hit)==0
    assert choose_drag_layer(m.parts,0,65,65,hit) is None


def test_asset_reposition_keeps_second_move_and_existing_pose_unchanged():
    m=make_model()
    first=m.insert_frame('Idle / Breathing',0)
    assert first==0
    earlier=m.render(m.animations['Idle / Breathing'][0]).tobytes()
    second_png=m.render_part(1,m.resolved_pose()[1]).tobytes()
    assert choose_drag_layer(m.parts,0,12,12,lambda i,x,y:exact_hit(m,i,x,y))==0
    m.move_with_children(0,4,0)
    assert m.render_part(1,m.resolved_pose()[1]).tobytes()==second_png
    assert m.render(m.animations['Idle / Breathing'][0]).tobytes()==earlier
    assert m.render().getpixel((16,12))==(240,30,30,255)
