import tempfile
import unittest
from pathlib import Path
from PIL import Image
from studio.pet_suite_model import PetSuiteModel
from studio.edit_history import EditHistory


class LayerRigIntegrationTests(unittest.TestCase):
    def make_model(self):
        m = PetSuiteModel((80, 80))
        for name, color in [('Body', 'red'), ('Arm', 'green'), ('Charm', 'blue')]:
            m.import_part(name, Image.new('RGBA', (6, 6), color))
        for i, part in enumerate(m.parts):
            part['x'] = 10 + i * 12
            part['y'] = 20
            m.set_anchor(i, 3, 3)
        m.attach(1, 0)
        m.attach(2, 1)
        m.animations['Wave'] = [m.snapshot()]
        m.move_with_children(0, 2, 0)
        m.rotate_part(0, 90)
        m.animations['Wave'].append(m.snapshot())
        m.set_frame_duration('Wave', 0, 80)
        m.set_frame_duration('Wave', 1, 220)
        return m

    def test_layer_reorder_preserves_attachment_and_pose_render(self):
        m = self.make_model()
        before = [m.render(p).tobytes() for p in m.animations['Wave']]
        identities = [p['name'] for p in m.parts]
        self.assertTrue(m.reorder_part(0, 1))
        self.assertEqual([p['name'] for p in m.parts], [identities[1], identities[0], identities[2]])
        self.assertEqual(m.attachments[0]['parent'], 1)
        self.assertEqual(m.attachments[2]['parent'], 0)
        self.assertEqual([m.render(p).tobytes() for p in m.animations['Wave']], before)
        self.assertEqual(m.frame_durations['Wave'], [80, 220])

    def test_reorder_undo_redo_then_save_load(self):
        m = self.make_model()
        history = EditHistory()
        baseline = m.content_fingerprint()
        history.record(m)
        m.reorder_part(1, 1)
        changed = m.content_fingerprint()
        self.assertNotEqual(changed, baseline)
        self.assertTrue(history.undo(m))
        self.assertEqual(m.content_fingerprint(), baseline)
        self.assertTrue(history.redo(m))
        self.assertEqual(m.content_fingerprint(), changed)
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'creature.json'
            m.save_project(path)
            reopened = PetSuiteModel.load_project(path)
            self.assertEqual(reopened.content_fingerprint(), changed)
            self.assertEqual(reopened.render(reopened.animations['Wave'][1]).tobytes(),
                             m.render(m.animations['Wave'][1]).tobytes())

    def test_moving_parent_keeps_child_offsets_and_saved_pose(self):
        m = self.make_model()
        saved = m.render(m.animations['Wave'][0]).tobytes()
        before = [(p['x'], p['y']) for p in m.parts]
        m.move_with_children(0, 5, -3)
        for i, part in enumerate(m.parts):
            self.assertEqual((part['x'], part['y']), (before[i][0] + 5, before[i][1] - 3))
        self.assertEqual(m.render(m.animations['Wave'][0]).tobytes(), saved)

    def test_invalid_attachment_cannot_create_cycle(self):
        m = self.make_model()
        before = dict(m.attachments)
        with self.assertRaisesRegex(ValueError, 'loop'):
            m.attach(0, 2)
        self.assertEqual(m.attachments, before)

    def test_corrupt_cycle_cannot_partially_move_rig(self):
        m = self.make_model()
        m.attachments[0] = {'parent': 2, 'offset_x': 0, 'offset_y': 0}
        positions = [(p['x'], p['y']) for p in m.parts]
        with self.assertRaisesRegex(ValueError, 'Circular'):
            m.move_with_children(0, 10, 0)
        self.assertEqual([(p['x'], p['y']) for p in m.parts], positions)

    def test_detach_allows_independent_movement(self):
        m = self.make_model()
        m.detach(2)
        before = m.parts[2]['x']
        m.move_with_children(0, 7, 0)
        self.assertEqual(m.parts[2]['x'], before)

    def test_reorder_invalid_is_noop(self):
        m = self.make_model()
        fingerprint = m.content_fingerprint()
        self.assertFalse(m.reorder_part(0, -1))
        self.assertEqual(m.content_fingerprint(), fingerprint)
