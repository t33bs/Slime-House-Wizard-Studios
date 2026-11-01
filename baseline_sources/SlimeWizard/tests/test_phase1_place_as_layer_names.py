import ast
from pathlib import Path

def test_explicit_place_as_layer_uses_unique_names_and_new_part():
    source = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()
    tree = ast.parse(source)
    method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == '_slimer_commit')
    body = ast.get_source_segment(source, method)
    assert "while f'Slimer Layer {number:03d}' in existing:" in body
    assert "self.model.import_part(f'Slimer Layer {number:03d}',result)" in body
    assert "self.model.import_part('Slimer layer',result)" not in body
