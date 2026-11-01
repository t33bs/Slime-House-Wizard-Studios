"""Behavioral checks for the temporary transformed-layer Move Original guard."""
import ast
from pathlib import Path
from types import SimpleNamespace
from PIL import Image


def _guard():
    tree = ast.parse((Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text())
    method = next(node for cls in tree.body if isinstance(cls, ast.ClassDef)
                  for node in cls.body if isinstance(node, ast.FunctionDef)
                  and node.name == '_slimer_original_erase_safe')
    method.decorator_list = []
    exec(compile(ast.Module(body=[method], type_ignores=[]), '<guard>', 'exec'), scope := {})
    return scope[method.name]


def _editor(angle=0, dimensions=(4, 4), original=(4, 4), visible=True):
    return SimpleNamespace(model=SimpleNamespace(
        parts=[{'visible': visible, 'image': Image.new('RGBA', dimensions), 'x': 0, 'y': 0}],
        originals=[Image.new('RGBA', original)], angles={0: angle},
        resolved_pose=lambda: [{'visible': visible, 'angle': angle, 'width': dimensions[0], 'height': dimensions[1], 'x': 0, 'y': 0}]))


def test_move_original_allows_untransformed_layer():
    assert _guard()(_editor()) is True


def test_move_original_rejects_rotated_layer():
    assert _guard()(_editor(angle=45)) is False


def test_move_original_rejects_resized_layer():
    assert _guard()(_editor(dimensions=(8, 4))) is False


def test_invisible_transformed_layer_does_not_block_move():
    assert _guard()(_editor(angle=45, visible=False)) is True
