"""Guard the history fallback that keeps model and UI animation aligned."""
from pathlib import Path
import ast


def test_history_restore_explicitly_synchronizes_model_before_refresh():
    source = (Path(__file__).resolve().parents[1] / 'friendly_animator.py').read_text()
    tree = ast.parse(source)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and any(isinstance(x, ast.FunctionDef) and x.name == '_after_history_restore' for x in n.body))
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '_after_history_restore')
    assignments = [n for n in ast.walk(fn) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Attribute) and t.attr == 'current' and isinstance(t.value, ast.Attribute) and t.value.attr == 'model' for t in n.targets)]
    assert assignments, 'History restore must synchronize model.current with selector fallback'
    assert source.index('self.model.current = animation', source.index('def _after_history_restore')) < source.index('self._after_history_change()', source.index('def _after_history_restore'))
