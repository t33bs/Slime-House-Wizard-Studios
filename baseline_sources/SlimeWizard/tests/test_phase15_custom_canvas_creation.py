"""Custom canvas sizing must preserve each project’s independent geometry."""
import ast
from pathlib import Path
from studio.pet_suite_model import PetSuiteModel


def test_new_project_offers_custom_and_presets():
    source = Path(__file__).resolve().parents[1].joinpath('friendly_animator.py').read_text()
    tree = ast.parse(source)
    method = next(n for cls in tree.body if isinstance(cls, ast.ClassDef) for n in cls.body
                  if isinstance(n, ast.FunctionDef) and n.name == 'new_project')
    body = ast.get_source_segment(source, method)
    for option in ('128 × 128 (default)', '64 × 64', '256 × 256',
                   '512 × 512', '1024 × 1024', 'Custom width × height'):
        assert option in body
    assert 'PetSuiteModel((width, height))' in body
    assert 'if not ok:' in body


def test_rectangular_canvas_isolated_and_round_trips(tmp_path):
    custom = PetSuiteModel((320, 192))
    standard = PetSuiteModel()
    assert custom.render().size == (320, 192)
    assert standard.render().size == (128, 128)
    path = tmp_path / 'custom.json'
    custom.save_project(path)
    loaded = PetSuiteModel.load_project(path)
    assert loaded.size == (320, 192)
    assert loaded.render().size == (320, 192)
