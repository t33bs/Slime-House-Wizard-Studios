"""Attached child transforms must be checked after parent transforms resolve."""
from test_slimer_transform_guard_cases import _guard, _editor

def test_inherited_parent_rotation_blocks_destructive_move():
    editor = _editor()
    editor.model.resolved_pose = lambda: [{'visible': True, 'angle': 90, 'width': 4, 'height': 4, 'x': 0, 'y': 0}]
    assert _guard()(editor) is False

def test_inherited_translation_allows_exact_pixel_mapping():
    editor = _editor()
    editor.model.resolved_pose = lambda: [{'visible': True, 'angle': 0, 'width': 4, 'height': 4, 'x': 2, 'y': 0}]
    assert _guard()(editor) is True
