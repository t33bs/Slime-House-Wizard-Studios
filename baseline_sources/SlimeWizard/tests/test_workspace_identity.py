import unittest
from studio.workspace_identity import animation_key,parse_animation_key,belongs_to_project

class WorkspaceIdentityTests(unittest.TestCase):
    def test_same_animation_different_creatures(self):
        self.assertNotEqual(animation_key(1,'Walking'),animation_key(2,'Walking'))
    def test_roundtrip(self):
        self.assertEqual(parse_animation_key(animation_key(3,'Idle::Custom')),(3,'Idle::Custom'))
    def test_ownership(self):
        self.assertTrue(belongs_to_project(animation_key(2,'Sleep'),2))
        self.assertFalse(belongs_to_project(animation_key(2,'Sleep'),1))
    def test_invalid(self):
        with self.assertRaises(ValueError):animation_key(-1,'Idle')
        with self.assertRaises(ValueError):parse_animation_key(('phase','Rigging'))
