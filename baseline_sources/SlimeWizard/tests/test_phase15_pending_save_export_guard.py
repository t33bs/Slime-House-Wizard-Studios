"""Regression contract: staged Slimer assets must not leak into disk exports."""
import ast
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'friendly_animator.py'
TREE = ast.parse(SOURCE.read_text(encoding='utf-8'))

def body_of(name):
    for node in ast.walk(TREE):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return ast.unparse(node)
    raise AssertionError(name)

def test_save_blocks_pending_layer_before_pose_save_or_dialog():
    body = body_of('save_project_by_id')
    assert "getattr(self, '_slimer_pending_part', None)" in body
    assert body.index("getattr(self, '_slimer_pending_part', None)") < body.index('self.preserve_pose_draft()')
    assert body.index("getattr(self, '_slimer_pending_part', None)") < body.index('getSaveFileName')

def test_sprite_sheet_export_blocks_pending_layer():
    body = body_of('export')
    assert "getattr(self, '_slimer_pending_part', None)" in body
    assert body.index("getattr(self, '_slimer_pending_part', None)") < body.index('self.preserve_pose_draft()')
