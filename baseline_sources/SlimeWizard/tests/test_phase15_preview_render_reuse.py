import ast
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1].joinpath('friendly_animator.py').read_text()
TREE = ast.parse(SOURCE)
SUITE = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == 'Suite')


def test_live_preview_reuses_render_without_saved_pose():
    method = next(n for n in SUITE.body if isinstance(n, ast.FunctionDef) and n.name == 'refresh_preview')
    assert len(method.args.args) == 2
    assert method.args.args[1].arg == 'current_render'
    assert 'pose is None and isinstance(current_render, Image.Image)' in ast.get_source_segment(SOURCE, method)


def test_refresh_preserves_unmodified_live_render_before_editor_overlays():
    method = next(n for n in SUITE.body if isinstance(n, ast.FunctionDef) and n.name == 'refresh')
    body = ast.get_source_segment(SOURCE, method)
    assert body.index('live_render=self.model.render()') < body.index('if self.onion.isChecked():')
    assert 'composed=live_render' in body
    assert 'if composed is live_render:' in body
    assert 'composed=live_render.copy()' in body
    assert 'self.refresh_preview(live_render)' in body


def test_saved_pose_still_uses_independent_render():
    method = next(n for n in SUITE.body if isinstance(n, ast.FunctionDef) and n.name == 'refresh_preview')
    assert 'else self.model.render(pose)' in ast.get_source_segment(SOURCE, method)
