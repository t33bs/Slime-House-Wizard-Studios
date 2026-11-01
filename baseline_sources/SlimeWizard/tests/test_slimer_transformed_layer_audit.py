"""Audit guard: transformed rendering must be accounted for before source erasure."""
import ast
from pathlib import Path


def test_erase_originals_has_explicit_transform_guard():
    tree = ast.parse((Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text())
    funcs = [node for cls in tree.body if isinstance(cls, ast.ClassDef)
             for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == '_slimer_erase_original_layers']
    assert len(funcs) == 1
    body = ast.unparse(funcs[0])
    assert '_slimer_original_erase_safe' in (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()
    assert 'self.model.angles' in (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()
    assert 'self.model.originals' in body
