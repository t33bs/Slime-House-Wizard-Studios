import tempfile
import unittest
from pathlib import Path
from PIL import Image
from studio.pet_suite_model import PetSuiteModel

class TestModel(unittest.TestCase):
    def test_frame_size_and_original_survive_reopen(self):
        m=PetSuiteModel((64,64));m.import_part('Head',Image.new('RGBA',(8,8),'red'))
        m.resize_part(0,16,12);m.parts[0]['x']=7
        m.animations['Walking']=[m.snapshot()]
        m.resize_part(0,4,4);m.parts[0]['x']=3
        m.animations['Walking'].append(m.snapshot())
        self.assertEqual(m.render(m.animations['Walking'][0]).getbbox(),(7,0,23,12))
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'creature.json';m.save_project(p);loaded=PetSuiteModel.load_project(p)
            self.assertEqual(loaded.originals[0].size,(8,8))
            self.assertEqual(loaded.render(loaded.animations['Walking'][0]).getbbox(),(7,0,23,12))
            self.assertEqual(loaded.render(loaded.animations['Walking'][1]).getbbox(),(3,0,7,4))
            self.assertTrue(loaded.export(d).exists())
    def test_attachment_moves_children_and_survives_save(self):
        m=PetSuiteModel((64,64))
        for name in ('Body','Head','Hat'):
            m.import_part(name,Image.new('RGBA',(8,8),'red'))
        m.parts[1]['x']=10;m.parts[2]['x']=12
        m.attach(1,0);m.attach(2,1)
        m.move_with_children(0,4,3)
        self.assertEqual([(p['x'],p['y']) for p in m.parts],[(4,3),(14,3),(16,3)])
        with self.assertRaises(ValueError):m.attach(0,2)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'cat.json';m.save_project(path)
            loaded=PetSuiteModel.load_project(path)
            loaded.move_with_children(0,2,0)
            self.assertEqual(loaded.parts[2]['x'],18)
        m.reorder_part(0,1)
        m.move_with_children(1,1,0)
        self.assertEqual(m.parts[0]['x'],15)

    def test_joint_dots_survive_reorder_and_reopen(self):
        m=PetSuiteModel((64,64))
        m.import_part('Body',Image.new('RGBA',(12,10),'red'))
        m.import_part('Head',Image.new('RGBA',(8,8),'blue'))
        m.parts[1]['x']=14
        m.set_anchor(1,2,3)
        self.assertEqual(m.anchor_position(1),(16,3))
        m.reorder_part(1,-1)
        self.assertEqual(m.anchor_position(0),(16,3))
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'pet.json';m.save_project(path)
            loaded=PetSuiteModel.load_project(path)
            self.assertEqual(loaded.anchors[0],[2,3])
            self.assertEqual(loaded.anchor_position(0),(16,3))

    def test_rotation_about_joint_and_saved_frame(self):
        m=PetSuiteModel((40,40))
        m.import_part('Arm',Image.new('RGBA',(4,12),'red'))
        m.parts[0]['x']=15;m.parts[0]['y']=10
        m.set_anchor(0,2,2)
        before=m.anchor_position(0)
        m.rotate_part(0,90)
        pose=m.snapshot()
        self.assertEqual(pose[0]['angle'],90)
        self.assertEqual(m.anchor_position(0),before)
        self.assertNotEqual(m.render().getbbox(),(15,10,19,22))
        m.animations['Wave']=[pose]
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'pet.json';m.save_project(path)
            loaded=PetSuiteModel.load_project(path)
            self.assertEqual(loaded.angles[0],90)
            self.assertEqual(loaded.animations['Wave'][0][0]['angle'],90)
            self.assertEqual(loaded.render().tobytes(),m.render().tobytes())
        m.reorder_part(0,1) if len(m.parts)>1 else None

    def test_connected_parts_follow_parent_rotation_and_reopen(self):
        m=PetSuiteModel((96,96))
        for name,color in [('Body','red'),('Arm','green'),('Hand','blue')]:
            m.import_part(name,Image.new('RGBA',(4,4),color))
        m.parts[0]['x']=30;m.parts[0]['y']=30
        m.parts[1]['x']=40;m.parts[1]['y']=30
        m.parts[2]['x']=50;m.parts[2]['y']=30
        for i in range(3):m.set_anchor(i,2,2)
        m.attach(1,0);m.attach(2,1)
        m.rotate_part(0,90)
        resolved=m.resolved_pose()
        self.assertEqual((resolved[1]['x'],resolved[1]['y']), (30,20))
        self.assertEqual((resolved[2]['x'],resolved[2]['y']), (30,10))
        self.assertEqual((resolved[1]['angle'],resolved[2]['angle']), (90,90))
        self.assertEqual(m.parts[1]['x'],40) # editable data remains unchanged
        m.animations['Wave']=[m.snapshot()]
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'pet.json';m.save_project(path)
            loaded=PetSuiteModel.load_project(path)
            self.assertEqual(loaded.resolved_pose(loaded.animations['Wave'][0]),resolved)
            self.assertEqual(loaded.render().tobytes(),m.render().tobytes())

    def test_reorder_preserves_frame_asset_identity(self):
        m=PetSuiteModel();m.import_part('a',Image.new('RGBA',(3,3),'red'));m.import_part('b',Image.new('RGBA',(5,5),'blue'))
        m.animations['Idle']=[m.snapshot()]
        self.assertTrue(m.reorder_part(0,1));self.assertEqual(m.parts[0]['name'],'b')
        self.assertEqual(m.animations['Idle'][0][0]['name'],'b')

if __name__=='__main__':unittest.main()

class TestTimelineEditing(unittest.TestCase):
    def test_copy_insert_shift_delete_and_save(self):
        m=PetSuiteModel((64,64));m.import_part('Head',Image.new('RGBA',(8,8),'green'))
        m.parts[0]['x']=4
        m.insert_frame('Walk',0)
        m.copy_frame('Walk',0)
        m.animations['Walk'][1][0]['x']=12
        self.assertEqual(m.animations['Walk'][0][0]['x'],4)
        self.assertEqual(m.move_frame('Walk',1,-1),0)
        self.assertEqual(m.animations['Walk'][0][0]['x'],12)
        m.delete_frame('Walk',1)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'pet.json';m.save_project(path)
            reopened=PetSuiteModel.load_project(path)
            self.assertEqual(len(reopened.animations['Walk']),1)
            self.assertEqual(reopened.animations['Walk'][0][0]['x'],12)

    def test_invalid_operations_are_safe(self):
        m=PetSuiteModel()
        self.assertEqual(m.move_frame('Idle',0,1),0)
        with self.assertRaises(IndexError):m.copy_frame('Idle',0)
        with self.assertRaises(IndexError):m.delete_frame('Idle',0)
