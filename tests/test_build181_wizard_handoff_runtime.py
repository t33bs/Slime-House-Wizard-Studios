"""Build 1.8.1: real Wizard reload method behavior, executable without a Qt GUI.

A prior GitHub patch shipped the new host/test but missed this Wizard file.
We exercise the actual method, not only a source-code substring.
"""
import ast
from pathlib import Path
from types import SimpleNamespace

from PIL import Image

from shws_wizard.studio.pet_suite_model import PetSuiteModel

ROOT = Path(__file__).resolve().parents[1]
WIZARD = ROOT / 'shws_wizard' / 'friendly_animator.py'


def load_wizard_reload_method():
    source = ast.parse(WIZARD.read_text(encoding='utf-8'), filename=str(WIZARD))
    suite = next(node for node in source.body if isinstance(node, ast.ClassDef) and node.name == 'Suite')
    method = next(node for node in suite.body
                  if isinstance(node, ast.FunctionDef) and node.name == 'reload_shs_edit')
    module = ast.Module(body=[method], type_ignores=[])
    ast.fix_missing_locations(module)
    class MessageBox:
        notices = []
        @classmethod
        def information(cls, *args): cls.notices.append(('info', args[-2:]))
        @classmethod
        def warning(cls, *args): cls.notices.append(('warning', args[-2:]))
    env = {'Image': Image, 'QMessageBox': MessageBox}
    exec(compile(module, str(WIZARD), 'exec'), env)
    return env['reload_shs_edit'], MessageBox


def make_editor(tmp_path):
    model = PetSuiteModel((128, 128))
    initial = Image.new('RGBA', (128, 128))
    initial.putpixel((9, 9), (10, 70, 160, 255))
    model.import_part('Creature', initial)
    for x in (0, 2, 5):
        model.parts[0]['x'] = x
        model.save_frame('Walk')
    model.current = 'Walk'
    target = 1
    pose_id = model.pose_id('Walk', target)
    edited = Image.new('RGBA', (128, 128))
    edited.putpixel((44, 44), (224, 15, 64, 255))
    path = tmp_path / 'edited.png'
    edited.save(path)
    notices = []
    calls = []
    editor = SimpleNamespace(
        _shs_edit=(str(path), 'test-project', 'Walk', target),
        _active_project_id='test-project', _shs_pose_id=pose_id,
        frame=target, model=model, anim=SimpleNamespace(currentText=lambda: 'Walk'),
        _next_pose_capture_pending=False,
        _slimer_pending_part=None, _slimer_pending_layer=None,
        preserve_pose_draft=lambda: calls.append('preserve'),
        remember=lambda: calls.append('remember'),
        assets=SimpleNamespace(addItem=lambda s: calls.append('add'),
                               setCurrentRow=lambda n: calls.append('select')),
        _saved_pose_key=lambda *args: ('saved', *args),
        _apply_saved_pose=lambda *args: calls.append('apply'),
        refresh_timeline=lambda: calls.append('refresh_timeline'),
        refresh=lambda: calls.append('refresh'),
        status=SimpleNamespace(setText=lambda s: notices.append(s)),
    )
    return editor, edited, calls


def test_identity_mismatch_fails_without_any_mutation(tmp_path):
    reload, messages = load_wizard_reload_method()
    editor, _edited, calls = make_editor(tmp_path)
    before = [editor.model.render(p).tobytes() for p in editor.model.animations['Walk']]
    editor._shs_pose_id = 'reordered-or-replaced-pose'
    messages.notices.clear()
    assert reload(editor) is False
    assert any(kind == 'warning' for kind, _ in messages.notices)
    assert not calls
    assert len(editor.model.animations['Walk']) == 3
    assert [editor.model.render(p).tobytes() for p in editor.model.animations['Walk']] == before


def test_unfinished_wizard_move_fails_closed(tmp_path):
    reload, _messages = load_wizard_reload_method()
    editor, _edited, calls = make_editor(tmp_path)
    before = [editor.model.render(p).tobytes() for p in editor.model.animations['Walk']]
    editor._slimer_pending_part = object()
    assert reload(editor) is False
    assert not calls
    assert [editor.model.render(p).tobytes() for p in editor.model.animations['Walk']] == before


def test_verified_png_replaces_only_original_pose_and_reports_success(tmp_path):
    reload, messages = load_wizard_reload_method()
    editor, edited, calls = make_editor(tmp_path)
    before = [editor.model.render(p).tobytes() for p in editor.model.animations['Walk']]
    ids = editor.model._sync_pose_ids('Walk')[:]
    durations = [editor.model.frame_duration('Walk', i) for i in range(3)]
    messages.notices.clear()
    assert reload(editor) is True
    assert not messages.notices
    assert calls == ['preserve', 'remember', 'add', 'apply', 'select', 'refresh_timeline', 'refresh']
    assert len(editor.model.animations['Walk']) == 3
    assert editor.model._sync_pose_ids('Walk') == ids
    assert [editor.model.frame_duration('Walk', i) for i in range(3)] == durations
    assert editor.model.render(editor.model.animations['Walk'][1]).tobytes() == edited.tobytes()
    for index in (0, 2):
        assert editor.model.render(editor.model.animations['Walk'][index]).tobytes() == before[index]
