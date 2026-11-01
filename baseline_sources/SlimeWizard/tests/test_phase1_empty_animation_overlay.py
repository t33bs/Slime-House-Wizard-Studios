"""Regression checks for Slimer overlay isolation on empty animation switches."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_empty_animation_switch_hides_only_slimer_overlay():
    tree = ast.parse((ROOT / 'friendly_animator.py').read_text())
    app = next(n for n in tree.body if isinstance(n, ast.ClassDef) and any(
        isinstance(m, ast.FunctionDef) and m.name == 'change_anim' for m in n.body))
    method = next(m for m in app.body if isinstance(m, ast.FunctionDef) and m.name == 'change_anim')
    source = ast.get_source_segment((ROOT / 'friendly_animator.py').read_text(), method)
    assert "part.get('name') == 'Slimer pose overlay'" in source
    assert "part['visible'] = False" in source
    assert 'if previous_animation != name:' in source


def test_saved_snapshot_is_unchanged_when_live_overlay_hidden():
    from PIL import Image
    from studio.pet_suite_model import PetSuiteModel
    model = PetSuiteModel()
    image = Image.new('RGBA', model.size, (30, 70, 220, 160))
    model.import_part('Slimer pose overlay', image)
    model.insert_frame('Idle', 0)
    before = model.animations['Idle'][0][0]['source_png']
    model.parts[0]['visible'] = False
    assert model.animations['Idle'][0][0]['source_png'] == before
    model.apply_pose(model.animations['Idle'][0])
    assert model.parts[0]['visible'] is True
    assert model.originals[0].getpixel((0, 0)) == (30, 70, 220, 160)
