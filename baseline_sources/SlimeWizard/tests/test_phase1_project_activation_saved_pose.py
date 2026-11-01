"""Project tab activation must load saved pose pixels before resetting Slimer."""
import ast
from pathlib import Path
from PIL import Image
from studio.pet_suite_model import PetSuiteModel

ROOT = Path(__file__).resolve().parents[1]


def test_project_activation_loads_pose_before_slimer_source_capture():
    source = (ROOT / 'friendly_animator.py').read_text()
    tree = ast.parse(source)
    method = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == 'activate_project')
    body = ast.get_source_segment(source, method)
    assert body.index('self._apply_saved_pose(animation,index)') < body.index('self._reset_slimer_for_project_change()')
    assert "self._project_timeline_index[self._active_project_id] = self.frame" in body
    assert "self.steps" not in body


def test_switching_to_empty_animation_hides_stale_overlay():
    source = (ROOT / 'friendly_animator.py').read_text()
    tree = ast.parse(source)
    method = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == 'activate_project')
    body = ast.get_source_segment(source, method)
    assert "if part.get('name') == 'Slimer pose overlay':" in body
    assert "part['visible'] = False" in body


def test_reapplying_saved_pose_restores_correct_rgba():
    model = PetSuiteModel()
    model.import_part('Slimer pose overlay', Image.new('RGBA', model.size, (10, 20, 30, 180)))
    model.insert_frame('Idle', 0)
    expected = model.render(model.animations['Idle'][0]).tobytes()
    model.originals[0] = Image.new('RGBA', model.size, (200, 100, 40, 255))
    model.parts[0]['image'] = model.originals[0].copy()
    model.apply_pose(model.animations['Idle'][0])
    assert model.render().tobytes() == expected
