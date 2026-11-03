"""Windows/Qt click-path: custom frame name, cancel, correct status, no stray prefixes."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import json
from pathlib import Path

import pytest
from PIL import Image
pytest.importorskip('PySide6')
from PySide6.QtWidgets import QApplication
import shws_wizard.friendly_animator as wizard


def test_export_all_frames_uses_custom_manifest_name(tmp_path, monkeypatch):
    app=QApplication.instance() or QApplication([])
    editor=wizard.Suite()
    # CI has no person to answer the normal unsaved-creature close dialog.
    # Skip that prompt for teardown only; production close behavior is unchanged.
    monkeypatch.setattr(editor, 'confirm_unsaved_projects', lambda *_a, **_kw: True)
    editor.show(); app.processEvents()
    try:
        editor.model.import_part('old-project-name',Image.new('RGBA',(4,4),(42,53,64,255)))
        editor.model.save_frame('Idle / Breathing')
        filename=tmp_path/'MySwordcat_frames.json'
        calls=[]
        def save_dialog(*args):
            calls.append(args)
            return str(filename), 'Animation frame manifest (*.json)'
        monkeypatch.setattr(wizard.QFileDialog,'getSaveFileName',save_dialog)
        editor.export_all_frames()
        assert calls
        assert calls[0][2] == 'creature_frames.json'
        assert filename.exists()
        assert (tmp_path/'MySwordcat_frame_0001.png').exists()
        manifest=json.loads(filename.read_text())
        assert manifest['frames'][0]['file']=='MySwordcat_frame_0001.png'
        assert 'MySwordcat' in editor.status.text()
        assert not list(tmp_path.glob('friendly*'))
    finally:
        editor.close()


def test_export_all_frames_cancel_leaves_files_untouched(tmp_path, monkeypatch):
    app=QApplication.instance() or QApplication([])
    editor=wizard.Suite()
    # Never leave a modal confirmation open when this GUI test cleans up.
    monkeypatch.setattr(editor, 'confirm_unsaved_projects', lambda *_a, **_kw: True)
    try:
        monkeypatch.setattr(wizard.QFileDialog,'getSaveFileName',lambda *a: ('',''))
        editor.export_all_frames()
        assert not list(tmp_path.iterdir())
    finally:
        editor.close()
