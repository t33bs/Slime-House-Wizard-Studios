"""Edit Selection must render one consistent source on large canvases."""
import ast
from pathlib import Path
from types import SimpleNamespace
from PIL import Image

SOURCE = Path(__file__).resolve().parents[1] / 'friendly_animator.py'
tree = ast.parse(SOURCE.read_text())
fn = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
          and node.name == 'slimer_create_editable_layer')
ns = {}
exec(compile(ast.Module(body=[fn], type_ignores=[]), str(SOURCE), 'exec'), ns)


class CounterModel:
    def __init__(self, image):
        self.image = image
        self.parts = []
        self.calls = 0

    def render(self):
        self.calls += 1
        return self.image.copy()

    def import_part(self, name, image):
        self.parts.append({'name': name, 'image': image})


class Status:
    def __init__(self):
        self.message = ''

    def setText(self, value):
        self.message = value


class Toggle:
    def __init__(self, value):
        self.value = value

    def isChecked(self):
        return self.value

    def setEnabled(self, value):
        pass


class AssetList:
    def __init__(self):
        self.items = []

    def addItem(self, name):
        self.items.append(name)

    def setCurrentRow(self, index):
        pass


def make_editor(image, snapshot=None):
    mask = Image.new('L', image.size, 0)
    mask.putpixel((2, 2), 255)
    model = CounterModel(image)
    editor = SimpleNamespace(
        _slimer_pending_layer=None,
        slimer_selection=SimpleNamespace(mask=mask, source=snapshot or image.copy()),
        model=model,
        status=Status(),
        slimer_move_original=Toggle(False),
        _slimer_visible_selection_mask=lambda m, source: Image.new('L', m.size, 255),
        remember=lambda: None,
        assets=AssetList(),
        canvas=SimpleNamespace(slimer_transform_mode=True),
        refresh=lambda: None,
    )
    return editor


def test_edit_selection_renders_only_once_and_stages_same_snapshot():
    image = Image.new('RGBA', (512, 512))
    image.putpixel((2, 2), (21, 42, 63, 255))
    editor = make_editor(image)
    assert ns['slimer_create_editable_layer'](editor) is True
    assert editor.model.calls == 1
    assert editor._slimer_pending_source.tobytes() == image.tobytes()
    assert editor.model.parts[0]['image'].getpixel((2, 2)) == (21, 42, 63, 255)


def test_stale_selection_rejected_without_creating_layer():
    image = Image.new('RGBA', (256, 256))
    image.putpixel((2, 2), (21, 42, 63, 255))
    editor = make_editor(image, snapshot=Image.new('RGBA', image.size))
    assert ns['slimer_create_editable_layer'](editor) is False
    assert editor.model.calls == 1
    assert not editor.model.parts
    assert 'source changed' in editor.status.message
