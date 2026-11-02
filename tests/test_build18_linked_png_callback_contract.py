"""Runtime behavior of the SHS linked-PNG callback, without requiring Qt.

The real Windows Qt click-through is additionally checked in
`test_build15_hotkeys_handoff_gui.py`. This test executes the unchanged
source method with minimal test doubles to catch a missing signal on Linux.
"""
import ast
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]


def get_save_method():
    source = (ROOT / 'studio/app.py').read_text(encoding='utf-8')
    tree = ast.parse(source)
    editor = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'MainWindow')
    fn = next(n for n in editor.body if isinstance(n, ast.FunctionDef) and n.name == 'save_external_png')
    module = ast.Module(body=[fn], type_ignores=[])
    ast.fix_missing_locations(module)
    return compile(module, str(ROOT / 'studio/app.py'), 'exec')


class FakeBox:
    warnings = []
    @classmethod
    def warning(cls, _window, title, text):
        cls.warnings.append((title, text))
    @classmethod
    def information(cls, *_args):
        raise AssertionError('A linked PNG was set; no information prompt expected')


def run_scenario(tmp_path, exporter, callback):
    messages = []
    editor = SimpleNamespace(
        external_png_path=str(tmp_path / 'frame.png'),
        layers=['fake-layer'], size_px=(128, 128), _dirty=True,
        _validate_still_export=lambda *_: True,
        _linked_png_save_callback=callback,
        statusBar=lambda: SimpleNamespace(showMessage=lambda *args: messages.append(args)),
    )
    env = {'Path': Path, 'QMessageBox': FakeBox, 'safe_export': exporter,
           'composite': lambda *args: SimpleNamespace(save=lambda *args, **kwargs: None)}
    exec(get_save_method(), env)
    FakeBox.warnings.clear()
    outcome = env['save_external_png'](editor)
    return outcome, editor, messages, FakeBox.warnings[:]


def test_save_completes_then_calls_host_exactly_once(tmp_path):
    events = []
    def fake_export(destination, generator, validator):
        events.append(('verified', destination))
        assert validator() is True
        generator(destination)
    def callback(destination):
        events.append(('returned', destination))
    result, editor, messages, warnings = run_scenario(tmp_path, fake_export, callback)
    assert result is True
    assert [ev[0] for ev in events] == ['verified', 'returned']
    assert events[0][1] == events[1][1]
    assert editor._dirty is False
    assert messages and not warnings


def test_failed_save_does_not_call_host_or_clear_dirty(tmp_path):
    called = []
    def failed_export(*args):
        raise OSError('disk full')
    result, editor, _messages, warnings = run_scenario(tmp_path, failed_export, called.append)
    assert result is False
    assert called == []
    assert editor._dirty is True
    assert warnings[0][0] == 'Save linked PNG failed'


def test_failed_handoff_reports_saved_png_accurately(tmp_path):
    def fine_export(*_):
        pass
    def broken_callback(_):
        raise RuntimeError('pose identity mismatched')
    result, editor, messages, warnings = run_scenario(tmp_path, fine_export, broken_callback)
    assert result is False
    assert editor._dirty is False  # the PNG save did succeed
    assert messages
    assert warnings[0][0] == 'PNG saved; Wizard return failed'


def test_standalone_shs_without_host_callback_still_saves(tmp_path):
    result, editor, _messages, warnings = run_scenario(tmp_path, lambda *_: None, None)
    assert result is True
    assert editor._dirty is False
    assert not warnings


def test_host_binds_callback_before_first_frame_edit():
    src=(ROOT/'main.py').read_text(encoding='utf-8')
    assert 'self.studio._linked_png_save_callback = self._finish_shs_frame_handoff' in src
    assert 'self.studio.linked_png_saved.connect(' not in src
    assert 'self.studio.save_external_png()' in src
