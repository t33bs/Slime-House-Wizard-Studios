"""Rejected destructive frame placement must not commit a draft first."""
import ast
from pathlib import Path


def test_frame_commit_checks_destructive_preflight_before_saving_draft():
    source = Path(__file__).resolve().parents[1] / 'friendly_animator.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    method = next(node for cls in ast.walk(tree) if isinstance(cls, ast.ClassDef)
                  for node in cls.body if isinstance(node, ast.FunctionDef)
                  and node.name == '_slimer_commit')
    checks = [node.lineno for node in ast.walk(method) if isinstance(node, ast.Call)
              and isinstance(node.func, ast.Attribute)]
    def line_of(name):
        return min(node.lineno for node in ast.walk(method) if isinstance(node, ast.Call)
                   and isinstance(node.func, ast.Attribute) and node.func.attr == name)
    assert line_of('_slimer_original_erase_safe') < line_of('preserve_pose_draft')
    assert line_of('_slimer_original_erase_safe') < line_of('remember')
