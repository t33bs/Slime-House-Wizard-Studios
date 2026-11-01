"""Recipe-free save/open/export and history integration, without a Qt dependency."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

from studio.edit_history import EditHistory, capture
from studio.pet_suite_model import PetSuiteModel


def _model():
    model = PetSuiteModel((32, 32))
    model.import_part('user artwork', Image.new('RGBA', (3, 3), (24, 100, 220, 255)))
    for name, positions, durations in (
        ('Pooping', (1, 6), (90, 310)),
        ('My unusual movement', (3, 11), (170, 450)),
    ):
        for x, duration in zip(positions, durations):
            model.parts[0]['x'] = x
            index = model.save_frame(name)
            model.set_frame_duration(name, index, duration)
    return model


def test_save_open_then_undo_redo_and_export_preserves_legacy_and_custom_animations():
    model = _model()
    with TemporaryDirectory() as folder:
        root = Path(folder)
        path = root / 'project.json'
        model.save_project(path)
        reopened = PetSuiteModel.load_project(path)
        initial = reopened.content_fingerprint()
        history = EditHistory()
        history.record(reopened)
        reopened.parts[0]['x'] = 17
        reopened.set_frame_duration('Pooping', 0, 222)
        changed = capture(reopened)
        assert history.undo(reopened)
        assert reopened.content_fingerprint() == initial
        assert history.redo(reopened)
        assert capture(reopened) == changed
        assert history.undo(reopened)
        sheet = reopened.export(root / 'export', basename='animation')
        metadata = json.loads(sheet.with_suffix('.json').read_text())
        assert [(f['animation'], f['duration_ms']) for f in metadata['frames']] == [
            ('Pooping', 90), ('Pooping', 310),
            ('My unusual movement', 170), ('My unusual movement', 450),
        ]
        with Image.open(sheet) as atlas:
            for frame in metadata['frames']:
                r = frame['rect']
                actual = atlas.crop((r['x'], r['y'], r['x'] + r['w'], r['y'] + r['h']))
                expected = reopened.render(reopened.animations[frame['animation']][frame['frame']])
                assert actual.tobytes() == expected.tobytes()
        assert reopened.content_fingerprint() == initial


def test_history_branch_after_reopen_clears_redo_without_changing_saved_file():
    model = _model()
    with TemporaryDirectory() as folder:
        path = Path(folder) / 'project.json'
        model.save_project(path)
        original = path.read_bytes()
        reopened = PetSuiteModel.load_project(path)
        history = EditHistory()
        history.record(reopened)
        reopened.set_frame_duration('My unusual movement', 1, 999)
        assert history.undo(reopened)
        history.record(reopened)
        reopened.set_frame_duration('My unusual movement', 1, 222)
        assert not history.redo(reopened)
        assert reopened.frame_duration('My unusual movement', 1) == 222
        assert path.read_bytes() == original
        assert PetSuiteModel.load_project(path).frame_duration('My unusual movement', 1) == 450
