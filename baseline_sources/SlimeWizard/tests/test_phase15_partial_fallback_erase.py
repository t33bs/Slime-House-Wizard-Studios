"""Regression: fallback erasure must reject incomplete pixel consumption."""
import ast
from pathlib import Path


def test_fallback_erase_raises_when_mask_remains():
    source = Path(__file__).resolve().parents[1] / 'friendly_animator.py'
    module = ast.parse(source.read_text(encoding='utf-8'))
    methods = [n for n in ast.walk(module) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    erase = next(n for n in methods if n.name == '_slimer_erase_original_layers')
    final = erase.body[-1]
    assert isinstance(final, ast.If)
    assert isinstance(final.test, ast.Compare)
    assert isinstance(final.body[0], ast.Raise)
    assert 'remaining.getbbox() is not None' in ast.unparse(final.test)
