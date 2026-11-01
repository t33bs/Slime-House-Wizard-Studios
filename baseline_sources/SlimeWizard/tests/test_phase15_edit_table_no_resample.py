"""Regression: moving a Slimer layer in the asset table must not resample it."""
import ast
from pathlib import Path
from types import SimpleNamespace
from contextlib import nullcontext
from PIL import Image

SOURCE = Path(__file__).resolve().parents[1] / 'friendly_animator.py'
tree = ast.parse(SOURCE.read_text(encoding='utf-8'))
cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Suite')
method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'update_asset')
namespace = {'blocked_signals': lambda _: nullcontext()}
exec(compile(ast.Module(body=[method], type_ignores=[]), str(SOURCE), 'exec'), namespace)

class Spin:
    def __init__(self, value): self.n = value
    def value(self): return self.n
    def setValue(self, value): self.n = value

class Fake:
    update_asset = namespace['update_asset']
    def __init__(self):
        self.selected = 0
        self.model = SimpleNamespace(parts=[{'x': 0, 'y': 0, 'image': Image.new('RGBA', (16, 16))}],
                                     originals=[Image.new('RGBA', (16, 16))])
        self.x, self.y, self.w, self.h = Spin(0), Spin(0), Spin(16), Spin(16)
        self.lock = SimpleNamespace(isChecked=lambda: False)
        self._slimer_pending_part = self.model.parts[0]
        self.history_count = self.refresh_count = self.resize_count = 0
        def resize(i, w, h):
            self.resize_count += 1
            self.model.parts[i]['image'] = self.model.parts[i]['image'].resize((w, h))
        self.model.resize_part = resize
    def remember(self): self.history_count += 1
    def refresh(self): self.refresh_count += 1

def test_repeated_xy_changes_do_not_resample_layer():
    f = Fake()
    image = f.model.parts[0]['image']
    for x in range(1, 31):
        f.x.setValue(x)
        f.update_asset()
    assert f.model.parts[0]['image'] is image
    assert f.resize_count == 0
    assert f.history_count == 30
    assert f.refresh_count == 30
    f.update_asset()
    assert f.history_count == 30
    assert f.refresh_count == 30

def test_actual_size_change_resamples_once():
    f = Fake()
    f.w.setValue(24)
    f.update_asset()
    assert f.resize_count == 1
    assert f.model.parts[0]['image'].size == (24, 16)
    f.x.setValue(4)
    f.update_asset()
    assert f.resize_count == 1
